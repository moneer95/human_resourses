# Copyright (c) 2023, monir and contributors
# For license information, please see license.txt
import datetime

import frappe
from frappe.model.document import Document
from datetime import timedelta


class Attendance(Document):
    start_time = frappe.db.get_single_value('Attendance Settings', 'start_time')
    end_time = frappe.db.get_single_value('Attendance Settings', 'end_time')
    hours_threshold_absent = frappe.db.get_single_value('Attendance Settings', 'working_hours_threshold_for_absent')
    # get entry and exit grace values
    late_entry_grace = frappe.db.get_single_value('Attendance Settings', 'late_entry_grace_period')
    early_exit_grace = frappe.db.get_single_value('Attendance Settings', 'early_exit_grace_period')

    def before_submit(self):
        self.set_work_hours()

    def set_work_hours(self):
        # get check in and out then convert them to str
        check_in = timedelta(hours=int(self.check_in.split(":")[0]),
                             minutes=int(self.check_in.split(":")[1]))
        check_out = timedelta(hours=int(self.check_out.split(":")[0]),
                              minutes=int(self.check_out.split(":")[1]))

        # var late hours to add late values to it
        late_hours = timedelta(minutes=0)

        # check in conditions
        if check_in > self.start_time + timedelta(minutes=self.late_entry_grace):
            late_hours = (check_in - timedelta(minutes=self.late_entry_grace) - self.start_time)

        # check out conditions
        if check_out < self.end_time - timedelta(minutes=self.early_exit_grace):
            late_hours = self.end_time - (check_out + timedelta(minutes=self.early_exit_grace)) + late_hours

        # set values
        self.late_hours = str(late_hours)
        self.work_hours = (self.end_time - self.start_time) - late_hours

        # check if is absend
        if (self.end_time - self.start_time) - late_hours < timedelta(hours=self.hours_threshold_absent):
            self.status = "Absent"
