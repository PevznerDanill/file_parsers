from typing import List
import csv
import logging
from pprint import pprint


CSV_PATH = 'result.csv'

with open(CSV_PATH, 'r') as csv_file:
    reader = csv.reader(csv_file)
    FIELDS = list(reader)[0]


logging.basicConfig(filename='bad_values.log', filemode='w',
                    format='%(asctime)s - %(message)s', level=logging.INFO)


class PdfParser:
    csv_dict = {
        field: "" for field in FIELDS
    }

    row_dict = {}

    rows_to_write = []

    def __init__(self, table: List[List[str]]):
        self.data = table

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


