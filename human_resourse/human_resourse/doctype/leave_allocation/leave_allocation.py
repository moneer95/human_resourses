# Copyright (c) 2023, monir and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import date_diff


class LeaveAllocation(Document):
    def validate(self):
        self.date_validate()

    def date_validate(self):
        # check if start date is before end date
        if date_diff(self.to_date, self.from_date):
            frappe.throw("initial date is after end date!")

        from_exists = frappe.db.get_list("Leave Application",
                                         filters={"employee": self.employee,
                                                  "docstatus": 1,
                                                  "from_date": ("<=", self.from_date),
                                                  "to_date": (">=", self.from_date)})
        if from_exists:
            # There are overlapping leave applications
            frappe.throw("There is an active Application for this member")

        to_exists = frappe.db.get_list("Leave Application",
                                       filters={"employee": self.employee,
                                                "docstatus": 1,
                                                "from_date": ("<=", self.to_date),
                                                "to_date": (">=", self.to_date)})
        if to_exists:
            # There are overlapping leave applications
            frappe.throw("There is an active Application for this member")
