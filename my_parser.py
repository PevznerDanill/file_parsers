import csv
import logging
import re
import inspect
import os
from pprint import pprint
from typing import Dict
from datetime import datetime
from datetime import timedelta
from datetime import date


class MyParser:
    logging.basicConfig(filename='bad_values.log', filemode='w',
                        format='%(asctime)s - %(message)s', level=logging.INFO)

    logger = logging.getLogger(__name__)

    csv_path = 'result.csv'

    start_date = date(1970, 1, 1)

    end_date = date(2105, 12, 31)

    row_dict = {}

    file_fields = {}

    rows_to_write = []

    original_rows_list = []

    def get_result_fields(self):
        if self.csv_path:
            with open(self.csv_path, 'r') as csv_file:
                reader = csv.reader(csv_file)
                return list(reader)[0]

    def update_dict(self, file_dict):
        row_dict = {}
        for field_name, field_value in file_dict.items():
            if field_name.lower() in self.csv_fields:
                row_dict[field_name.lower()] = [str(field_value), False]
        if 'user_additional_info' not in row_dict:
            row_dict['user_additional_info'] = ()
        return row_dict

    def __init__(self):
        self.methods = [method[1] for method in inspect.getmembers(self, inspect.ismethod)]
        self.csv_fields = self.get_result_fields()
        self.func_map = self.update_func_map()

    def generate_csv(self):
        pass

    def write_rows(self):
        with open(self.csv_path, 'a') as file:
            writer = csv.DictWriter(file, fieldnames=self.csv_fields)
            for data in self.rows_to_write:
                writer.writerow(data)
        self.rows_to_write = []

    def update_func_map(self):
        func_map = {
            re.sub(r"_process", "", method.__name__): method
            for method in self.methods if "_process" in method.__name__
        }

        return func_map

    def tel_process(self):
        """
        Предполагая, что должно быть 11 цифр (или 10 если без начальной единицы),
        которые могут быть разделены знаками "-" или пробелами. Первые три цифры (со второй по четвертую,
        если есть единица) могут быть в кавычках.
        """
        tel = self.row_dict.get('tel')[0]
        pattern = r"(?:1(?:-|\s))?(?:\(?\d{3}\)?(?:\s|-))(?:\d{3}(?:\s|-))\d{4}"
        tel_check = re.fullmatch(pattern, tel)
        if tel_check:
            if ('(' in tel and ')' in tel) or ('(' not in tel and ')' not in tel):
                self.row_dict['tel'] = (self.correct_number(tel), True)
        else:
            self.logger.info(f"Bad phone number: {tel}")
            self.row_dict['tel'] = ("", True)

    def date_process(self):
        pdf_date = self.row_dict.get('date')[0]
        date_format = "%d %B %Y"

        try:
            date_obj = datetime.strptime(pdf_date, date_format)
        except ValueError:
            date_obj = None
        if date_obj and self.start_date <= date_obj.date() <= self.end_date:
            self.row_dict['date'] = (datetime.strftime(date_obj, "%Y-%m-%d"), True)
        else:
            self.row_dict['date'][1] = True
            self.logger.info(f"Bad date: {pdf_date}")

    def email_process(self):
        email = self.row_dict.get('email')[0]
        if not re.fullmatch(
            r"(?:[A-Za-z0-9]+[._])*[A-Za-z0-9]+@(?:[A-Za-z0-9-]+)(?<!-)(?:\.[A-Z|a-z]{2,})+",
            email
        ):
            self.logger.info(f"Bad email: {email}")
        self.row_dict['email'][1] = True

    @classmethod
    def correct_number(cls, number):
        digits = re.findall(r'\d', number)
        if len(digits) == 11:
            digits = digits[1:]
        return "1 ({}{}{}) {}{}{} {}{}{}{}".format(*digits)

    def zip_process(self):
        user_zip = self.row_dict.get('zip')[0]
        if not re.fullmatch(
            r"\d{5}(?:-\d{4})?", user_zip
        ):
            self.logger.info(f"Bad zip: {user_zip}")
            self.row_dict['zip'] = ("", True)
        else:
            self.row_dict['zip'][1] = True

    def address_process(self):
        """
        Предполагая следующие свойства адреса:
        - может или нет начинаться с Apt./Suite и номером квартиры;
        - название улицы может состоять из более одного слова, начинающиеся на заглавные буквы или цифру
        (например, 05th Avenue) и может содержать цифры и символы "-&'.";
        - название города может состоять из более одного слова, каждое из которых должно начинаться с
        заглавной, и содержать символы ".'";
        - код штата состоит из двух заглавных букв;
        - zip-код состоит из пяти цифр и может сопровождаться дополнительно дефисом и четырьмя
        цифрами
        """
        address = self.row_dict.get('address')[0]
        address_pattern = r"(?:(?:Apt\.\s)|(?:Suite\s)\d+\s)?\d+(?:\s[A-Z\d][A-Za-z\d.'&-]+)+,(?:\s[A-Z][A-Za-z.']+)+,\s[A-Z]{2}\s\d{5}(?:-\d{4})?"
        if not re.fullmatch(address_pattern, address):
            self.logger.info(f"Bad address: {address}")
            self.row_dict['address'] = ("", True)
        else:
            self.row_dict['address'][1] = True

    def name_process(self):
        name = self.row_dict.get('name')[0]
        if not re.fullmatch(r"[A-Z][a-z]+", name):
            self.logger.info(f"Bad name: {name}")
            self.row_dict['name'] = ("", True)
        else:
            self.row_dict['name'][1] = True

    def clean_row_dict(self, additional_info):
        self.row_dict = {
            field_name: field_value[0]
            for field_name, field_value in self.row_dict.items()
            if field_name in self.csv_fields and field_name != 'user_additional_info'
        }
        self.row_dict['user_additional_info'] = additional_info

    def process_row_dict(self):
        for field_name, func in self.func_map.items():
            if field_name in self.row_dict.keys():
                if self.row_dict[field_name][1] is False:
                    func.__call__()
        additional_info = "|".join(self.row_dict['user_additional_info'])
        self.clean_row_dict(additional_info)
        self.rows_to_write.append(self.row_dict)
        self.row_dict = {}
