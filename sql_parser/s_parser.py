import csv
import logging
from my_parser import MyParser
import re
from pprint import pprint
from typing import List, Union


class SqlParser(MyParser):

    def __init__(self, sql_content: List[Union[str, int]]):
        self.sql_content = sql_content
        self.generate_dict()
        super().__init__()

    def change_field_names(self, field_name):
        if field_name == 'userid':
            return re.sub(r'id', '_ID', field_name)
        if field_name == 'password':
            return 'userpass_plain'
        if field_name == 'birth':
            return 'dob'
        return field_name

    def generate_csv(self):
        for row_dict in self.original_rows_list:
            self.row_dict = self.update_dict(row_dict)
            pprint(self.row_dict)
            self.process_row_dict()

        self.write_rows()

    def update_dict(self, file_dict):
        row_dict = super().update_dict(file_dict)
        row_dict.update(file_dict)
        return row_dict

    def generate_dict(self):
        first_line_values = re.search(r"\([a-z`\s,]+\)", self.sql_content[0])[0]
        field_names = [
            self.change_field_names(field_name)
            for field_name in re.findall('`(\w+)`', first_line_values)
            if field_name != 'mobile'
        ]
        all_lines = self.sql_content[1:]
        for line in all_lines:
            target_line = line[1:-3]
            values = [
                [re.sub(r"'(.+)'", r"\1", value), False]
                for value in target_line.split(',\t')
            ]

            self.original_rows_list.append(
                dict(zip(field_names, values))
            )

    def show_dict(self):
        pprint(self.original_rows_list)

    def country_process(self):
        country = self.row_dict.get('country')[0]
        if not re.fullmatch(
            r"(?:[A-Z][a-z]+)(?:\s[A-za-z]+){,9}", country
        ):
            self.logger.info(f'Bad country name: {country}')
            self.row_dict['country'] = ("", True)
        else:
            self.row_dict['country'][1] = True

    def user_ID_process(self):
        pass


