import re
from typing import List
import csv
import logging
from pprint import pprint
from my_parser import MyParser
from datetime import datetime
from datetime import timedelta
from datetime import date


class PdfParser(MyParser):
    """
    Парсер для pdf файлов. Потомок MyParser.
    """
    def __init__(self, table: List[List[str]], chunks=None):
        """
        Перед родительским __init__ методом сохраняет данные pdf в виде списка.
        """
        self.data = table
        super().__init__(chunks=chunks)

    def update_dict(self, file_dict):
        """
        Добавляет оставшиеся поля к созданному в родительском методе row_dict.
        """
        row_dict = super().update_dict(file_dict)
        row_dict.update(file_dict)
        return row_dict

    def generate_csv(self):
        """
        Перед родительским методом вызывает data_to_dicts, где заполняется original_rows_list из self.table
        """
        self.data_to_dicts()
        super().generate_csv()

    def nationality_process(self) -> None:
        """
        Проверяет на валидность значение nationality и, если валидно, сохраняет его в user_additional_info
        """
        nationality = self.row_dict.get('nationality')[0]
        if re.fullmatch(
            r"(?:[A-ZÀ-Ü][a-zà-ü]+)(?:(?:\s\([A-ZÀ-Üa-zà-ü]+\))|(?:(?:\s|-)[A-ZÀ-Üa-zà-ü]+))*", nationality
        ):
            self.row_dict['user_additional_info'] += f'Национальность: {nationality}',
        else:
            self.logger.info(f'Bad nationality: {nationality}')
        self.row_dict['nationality'][1] = True

    def data_to_dicts(self):
        """
        Генерирует словари из списка данных из table и сохраняет в original_rows_list
        """
        count = 0
        new_row_dict = {}
        for data_list in self.data[1:]:
            new_row_dict[data_list[0]] = [str(data_list[1]), False]
            count += 1
            if count == 6:
                count = 0
                self.original_rows_list += new_row_dict,
                new_row_dict = {}
