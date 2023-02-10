# Copyright (c) 2023, monir and contributors
# For license information, please see license.txt
from datetime import datetime

import frappe.utils
import frappe
from frappe.model.document import Document


class Employee(Document):
	def validate(self):
		self.calc_age()
		self.validate_age()
		self.set_full_name()
		self.validate_education()

	def calc_age(self):
		self.age = (frappe.utils.getdate(frappe.utils.now()).year - frappe.utils.getdate(self.date_of_birth).year)

	def validate_age(self):
		if self.age >= 60 and self.status == 'active':
			frappe.throw("can not add employee with status active and age 60")

	def set_full_name(self):
		self.full_name = self.first_name + ' ' + self.middle_name + ' ' + self.last_name

	def validate_education(self):
		num_of_educations = 0
		if len(self.employee_education) < 2:
			frappe.throw("employee must have two educations at least")


