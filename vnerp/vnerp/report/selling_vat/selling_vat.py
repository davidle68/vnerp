# Copyright (c) 2013, Vinhbk2000 and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
from frappe.utils import get_first_day, get_last_day, add_to_date, nowdate, getdate, add_days, add_months

def execute(filters=None):
	if not filters: filters = {}

	#filters.from_date = get_first_day(filters["period_num"] + '-' + filters["year"])
	#filters.to_date = get_last_day(filters["period_num"] + '-' + filters["year"])

	if(filters.period=="Month"):
		#convert from_date
		filters.from_date = get_first_day(filters.period_num + '-' + filters.year)
		filters.to_date =  get_last_day(filters.period_num + '-' + filters.year)
		#frappe.msgprint(filters.from_date)
	
	if(filters.period=="Quarter"):
		#convert from_date
		period_num = "1"
		if(filters.period_num=="2"):
			period_num = "4"
		if(filters.period_num=="3"):
			period_num = "7"
		if(filters.period_num=="4"):
			period_num = "10"
			
		filters.from_date = get_first_day(period_num + '-' + filters.year)
		filters.to_date = add_months(filters.from_date, 3)
		filters.to_date = add_days(filters.to_date, -1)
		#frappe.msgprint(filters.from_date)


	address = frappe.get_doc("Address", filters.company)
	company = frappe.get_doc("Company", filters.company)

	data_to_be_printed = {
		"company": company,
		"address": address
	}

	columns = get_columns()
	data = get_invoices(filters)
	return columns, data, None, None, data_to_be_printed
	
def get_columns():
	return [
		"VAT Type::450",
		"Net Total:Currency:150", "Tax %:Percent:50",
		"Total Sales Tax Amount:Currency:150"
	]

def get_invoices(filters):
	conditions = get_conditions(filters)

	data = []

	#Purchase Invoice
	query = """ SELECT name, tax_rate FROM `tabAccount`
	WHERE `account_type`='Tax' 
	AND `freeze_account`='No' 
	AND `is_group` = 0 
	AND `name` LIKE '133%' 
	ORDER BY name """

	listAcount = frappe.db.sql(query, as_list=1)

	listAcount = frappe.db.sql(query, as_list=1)
	arrAcount = []
	arrTaxRate = []

	for i in range(0, len(listAcount)):
		arrAcount.append(listAcount[i][0])
		arrTaxRate.append(listAcount[i][1])

	for i in range(0, len(arrAcount)):
		rate_name = arrAcount[i]
		tax_rate = arrTaxRate[i]

		query = """SELECT si_tax.account_head,
		sum(si.base_net_total)*(-1), %d, sum(si_tax.base_tax_amount)*(-1)
		FROM `tabPurchase Invoice` si, `tabPurchase Taxes and Charges` si_tax
		WHERE si.docstatus = 1 AND si_tax.parent = si.name AND si_tax.account_head = '%s'
		%s
		GROUP BY si_tax.account_head
		""" %(tax_rate, rate_name, conditions)

	
		row = frappe.db.sql(query, as_list=1)

		if (row):
			data.append(row[0])
		else:
			data.append([rate_name, 0, tax_rate, 0])


	#Sales Invoice
	query = """ SELECT name, tax_rate FROM `tabAccount`
	WHERE `account_type`='Tax' 
	AND `freeze_account`='No' 
	AND `is_group` = 0 
	AND `name` LIKE '3331%' 
	ORDER BY name """

	listAcount = frappe.db.sql(query, as_list=1)
	arrAcount = []
	arrTaxRate = []

	for i in range(0, len(listAcount)):
		arrAcount.append(listAcount[i][0])
		arrTaxRate.append(listAcount[i][1])

	for i in range(0, len(arrAcount)):
		rate_name = arrAcount[i]
		tax_rate = arrTaxRate[i]

		query = """SELECT si_tax.account_head,
		sum(si.base_net_total), %d, sum(si_tax.base_tax_amount)
		FROM `tabSales Invoice` si, `tabSales Taxes and Charges` si_tax
		WHERE si.docstatus = 1 AND si_tax.parent = si.name AND si_tax.account_head = '%s'
		%s
		GROUP BY si_tax.account_head
		""" %(tax_rate, rate_name, conditions)

	
		row = frappe.db.sql(query, as_list=1)

		if (row):
			data.append(row[0])
		else:
			data.append([rate_name, 0, tax_rate, 0])
	
		#frappe.msgprint(query)
	
	#frappe.msgprint (data)
	#tin = frappe.db.sql ("""SELECT name, customer, tin_no from `tabAddress` """, as_list=1)
	
	#frappe.msgprint(len(si))
	
	# for i in range(0, len(si)):	
	# 	si[i][4] = si[i][4]-si[i][6]
	# 	for j in range(0,len(tin)):
	# 		if si[i][2]==tin[j][0]:
	# 			si[i][2]= tin[j][2]

	return data
	

def get_conditions(filters):
	conditions = ""

	if filters.get("from_date"):
		conditions += " and si.posting_date >= '%s'" % filters["from_date"]

	if filters.get("to_date"):
		conditions += " and si.posting_date <= '%s'" % filters["to_date"]
	
	return conditions	
