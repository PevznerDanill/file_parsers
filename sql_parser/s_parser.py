import csv
import logging
from my_parser import MyParser
import re
from pprint import pprint
from typing import List, Union
import itertools


class SqlParser(MyParser):

    def __init__(self, sql_content: List[Union[str, int]]):
        self.sql_content = sql_content
        self.generate_dict()
        self.get_date_formats()
        super().__init__()

    def get_date_formats(self):
        for new_format in self.date_formats_options:
            permutations = itertools.permutations(new_format)
            for perm in permutations:
                for symbol in self.symbols:
                    self.date_formats += f"{symbol}".join(perm),

    def sex_process(self):
        sex = self.row_dict.get("sex")[0]
        if re.fullmatch(
            r"M|F", sex
        ):
            if sex == 'M':
                str_to_append = 'Пол: мужской'
            else:
                str_to_append = 'Пол: женский'
            self.row_dict['user_additional_info'] += str_to_append,
        else:
            self.logger.info(f"Bad sex definition: {sex}")
        self.row_dict['sex'][1] = True

    @classmethod
    def change_field_names(cls, field_name):
        if field_name == 'userid':
            return re.sub(r'id', '_ID', field_name)
        if field_name == 'birth':
            return 'dob'
        return field_name

    def generate_csv(self):
        for row_dict in self.original_rows_list:
            self.row_dict = self.update_dict(row_dict)
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
            if not re.search(r"INSERT INTO", line):
                target_line = re.search(r"\((.+)\)", line).group(1)
                values = [
                    [re.sub(r"'(.+)'", r"\1", value), False]
                    for value in target_line.split(',\t')
                ]

                self.original_rows_list.append(
                    dict(zip(field_names, values))
                )

    def password_process(self):
        password = self.row_dict.get('password')[0]
        self.row_dict['user_additional_info'] += f'Хэш пароля: {password}',
        self.row_dict['password'][1] = True

    def show_dict(self):
        pprint(self.original_rows_list)





