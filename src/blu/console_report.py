from __future__ import print_function

import json
import logging
import os

from terminaltables import AsciiTable, DoubleTable, SingleTable

# mock data
# TODO to be removed
report_data = (
    ('name', 'resp_code', 'result', 'status', 'error', 'retry', 'link'),
    ('Example', 'xx', 'xx', 'S/F', 'xx', 'xx', 'xx'),
    )

SYSTEM_DATA = (
    ('Plateform', 'state', 'last try', 'since'),
    ('suntech', 'ok', '10:10:06', ' 3h'),
    ('wialon', 'recovering', '4:36:46', ' < day'),

)
title = 'Bluicity System Integration Report'


class ReportBuilder():

    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ReportBuilder.__instance == None:
            ReportBuilder()
        return ReportBuilder.__instance

    def __init__(self, raw_data=None):
        self.entries = {}
        self.data = raw_data
        self.filename = config.get_value(report_file)
        ReportBuilder.__instance = self

    def add(self, key, new_entry):
        """
        add a new entry to the report
        """
        self.entries[key] = new_entry
        return self.entries

    def update_data(self, data=None):
        """
        update all data set
        """
        self.data = data
        return self.data

    def delete_key(self, key):
        """
        remove an entry from the report
        """
        if key in self.entries:
            value = self.entries[key]
            del self.entries[key]
            return value

    @staticmethod
    def print_report(console=True, fail=None):
        """
        Print the report in 2 ways console, file
        fail only print the failling cases
        console show the report on standard oupt
        """        
        data = report_data
        table = AsciiTable(data, title)
        table.inner_row_border = True
        table.justify_columns[2] = 'right'
        if console:
            print()
            print(table.table)
            print()
        else:
            file_path = os.path.expanduser('~/bcity_pretty_report.txt')
            with open(file_path, 'w') as f:
                print(table.table, file=f)

    def _prep_data(self, data):
        """
        Prepare data from raw data.
        """
        # TODO implements
        return data

    @staticmethod
    def save_report(data=None, file_name=None):
        """
        Save report file
        """
        if not file_name:
            file_name = config.get_value(report_file)
        if not data:
            raise Exception("No data to be saved")
        file_path = os.path.expanduser(file_name)
        instance = ReportBuilder.getInstance()
        with open(file_path, 'w') as outfile:
            logging.debug("saving report data")
            json.dump(instance._prep_data(data), outfile)
        logging.debug("report saved successfully")
        return True

    @staticmethod
    def load_report_data(file_name=None):
        """
        Load report file
        """
        if not file_name:
            file_name = config.get_value(report_file)
        file_path = os.path.expanduser(file_name)
        with open(file_path, 'r') as outfile:
            logging.debug("loading data...")
            data = json.load(outfile)
            return data

    @staticmethod
    def build_report(report_file=None):
        """
        Build a report
        """
        global report_data
        data = ReportBuilder.load_report_data(file_name=report_file)
        _report = list(report_data)
        for key, item in data.items():
            _report.append(item)
        report_data = tuple(_report)

    @staticmethod
    def service_status():
        sys_table = SingleTable(SYSTEM_DATA, "Services")
        sys_table.justify_columns[2] = 'right'
        sys_table.inner_row_border = True
        sys_table.justify_columns = {0: 'center', 1: 'center', 2: 'center'}
        print(sys_table.table)
        print()


def main():
    """
    Main prog
    """
    builder = ReportBuilder.getInstance()
    builder.build_report()
    builder.print_report()
    builder.service_status()


if __name__ == '__main__':
    main()
