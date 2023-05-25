import re
from typing import List
import csv
import logging
from pprint import pprint
from my_parser import MyParser
from datetime import datetime
from datetime import timedelta
from datetime import date


CSV_PATH = 'result.csv'

with open(CSV_PATH, 'r') as csv_file:
    reader = csv.reader(csv_file)
    FIELDS = list(reader)[0]


logging.basicConfig(filename='bad_values.log', filemode='w',
                    format='%(asctime)s - %(message)s', level=logging.INFO)


class PdfParser(MyParser):
    csv_dict = {
        field: "" for field in FIELDS
    }

    row_dict = {}

    rows_to_write = []

    def __init__(self, table: List[List[str]]):
        self.data = table
        super().__init__()

    def update_dict(self, file_dict):
        row_dict = super().update_dict(file_dict)
        row_dict.update(file_dict)
        return row_dict

    def generate_csv(self):
        self.data_to_dicts()
        for row_dict in self.original_rows_list:
            self.row_dict = self.update_dict(row_dict)
            self.process_row_dict()

        self.write_rows()

    def nationality_process(self):
        nationality = self.row_dict.get('nationality')[0]
        if re.fullmatch(
            r"(?:[A-ZÀ-Ü][a-zà-ü]+)(?:(?:\s\([A-ZÀ-Üa-zà-ü]+\))|(?:(?:\s|-)[A-ZÀ-Üa-zà-ü]+))*", nationality
        ):
            self.row_dict['user_additional_info'] += f'Национальность: {nationality}',
        else:
            self.logger.info(f'Bad nationality: {nationality}')
        self.row_dict['nationality'][1] = True

    def data_to_dicts(self):
        count = 0
        new_row_dict = {}
        for data_list in self.data[1:]:
            new_row_dict[data_list[0]] = [str(data_list[1]), False]
            count += 1
            if count == 6:
                count = 0
                self.original_rows_list.append(new_row_dict)
                new_row_dict = {}

    def process_rows(self):
        for ind, row in enumerate(self.data[1:]):
            field = row[0]
            value = row[1]
            if field == 'nationality':
                self.row_dict['user_additional_info'] = f"Национальность: {value}"
            elif field == 'email':
                self.row_dict['usermail'] = value
                self.rows_to_write.append(self.row_dict)
                self.row_dict = {}
            else:
                self.row_dict[field] = value

        self.write_rows()

    def write_rows(self):
        with open(CSV_PATH, 'a') as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            for data in self.rows_to_write:
                writer.writerow(data)


