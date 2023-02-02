# Copyright (c) 2023, monir and contributors
# For license information, please see license.txt
import datetime

from frappe.utils import date_diff
import frappe
from frappe.model.document import Document


class LeaveApplication(Document):
    def validate(self):
        self.set_total_leave_days()
        self.calc_leave_allocation()
        self.validate_max_continuous_days()
        self.must_application_before()


    def before_submit(self):
        self.date_validate()

    def before_cancel(self):
        self.retriv_balance()

    def set_total_leave_days(self):
        if (self.from_date and self.to_date):
            self.total_leave_days = date_diff(self.to_date, self.from_date) + 1

    def calc_leave_allocation(self):
        if self.negative_balance_allowed():
            if self.leave_balance - self.total_leave_days >= 0:
                frappe.db.set_value('Leave Allocation', 'Leave Allocation for ' + self.employee_name,
                                    {'total_leaves_allocated': self.leave_balance - self.total_leave_days})
                self.leave_balance = frappe.db.get_value('Leave Allocation', 'Leave Allocation for ' + self.employee_name,
                                                         ['total_leaves_allocated'])
            else:
                frappe.throw("you have exceeded your leave balance!")

    def retriv_balance(self):
        frappe.db.set_value('Leave Allocation', 'Leave Allocation for ' + self.employee_name,
                            {'total_leaves_allocated': self.leave_balance + self.total_leave_days})

    def date_validate(self):
        if self.total_leave_days < 0:
            frappe.throw("initial date is after to date")

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


    def validate_max_continuous_days(self):
        allowed = frappe.db.get_value("Leave Type", f"{self.leave_type}", fieldname="max_continuous_leave_days")
        if self.total_leave_days > allowed:
            frappe.throw(f"max continuous leave days is {allowed} !")

    def negative_balance_allowed(self):
        return frappe.db.get_value("Leave Allocation", 'Leave Allocation for ' + self.employee_name, fieldname='allow_negative_balance')

    def must_application_before(self):
        allowed = frappe.db.get_value("Leave Type", f"{self.leave_type}", fieldname="must_application_before")
        if date_diff(datetime.datetime.now(), self.from_date) > allowed:
            frappe.throw(f"max continuous leave days is {allowed} !")
