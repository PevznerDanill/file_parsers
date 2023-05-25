import re
import csv
import logging
from my_parser import MyParser
from pandas.core.frame import DataFrame


CSV_PATH = 'result.csv'

with open(CSV_PATH, 'r') as csv_file:
    reader = csv.reader(csv_file)
    FIELDS = list(reader)[0]


class ExcelParser(MyParser):

    logging.basicConfig(filename='bad_values.log', filemode='w',
                        format='%(asctime)s - %(message)s', level=logging.INFO)

    """
    Класс для обработки данных из worksheet и их записи в csv файл.
    """

    rows_to_write = []

    def __init__(self, data_frame: DataFrame, chunks=None):
        self.data_frame = data_frame
        self.chunks = chunks
        super().__init__()

    def generate_csv(self):
        all_dicts = self.data_frame.to_dict(orient='records')
        if self.chunks:
            limit = 0
        else:
            limit = -1
        for ind, row_dict in enumerate(all_dicts):
            self.row_dict = self.update_dict(row_dict)
            self.process_row_dict()
            if limit >= 0:
                limit += 1
                if limit == self.chunks:
                    self.write_rows()
                    print(f'Wrote {ind + 1} rows')
                    limit = 0
        if len(self.rows_to_write) > 0:
            print(f'Writing remaining {len(self.rows_to_write)} rows')
            self.write_rows()
        print(f'Wrote all {ind+1} rows')

    def update_dict(self, file_dict):
        row_dict = super().update_dict(file_dict)
        new_dict = {
            re.sub(r"\s", "_", key.lower()): [str(value), False]
            for key, value in file_dict.items()
        }
        row_dict.update(new_dict)
        return row_dict

    def company_process(self):
        position = self.row_dict.get('position')[0]
        company = self.row_dict.get('company')[0]
        check_position = re.fullmatch(
            r"(?:[a-z]+)(?:\s[a-z]+)*",
            position
        )
        check_company = re.fullmatch(
            r"(?:[A-Z][A-Za-z']+)(?<!['-])(?:(?:(?:\s|-|,\s)(?!['-])[A-Za-z'-]+)(?<!['-]))*",
            company
        )
        str_to_append = None
        if check_company and check_position:
            str_to_append = f"Работает в компании {company} в отделе {self.row_dict['department']} " \
                            f"в должности {position}"
        elif check_company and check_position is None:
            self.logger.info(f"Bad position: {position}")
            str_to_append = f"Работает в компании {company} в отделе {self.row_dict['department']}"
        elif check_company is None and check_position:
            self.logger.info(f"Bad company: {company}")
            str_to_append = f"Работает в должности {position}"
        else:
            self.logger.info(f"Bad company: {company}")
            self.logger.info(f"Bad position: {position}")
        if str_to_append is not None:
            self.row_dict['user_additional_info'] += str_to_append,
        self.row_dict['company'][1] = True
        self.row_dict['position'][1] = True
        self.row_dict['department'][1] = True

    def mobile_number_process(self):
        self.row_dict['tel'] = self.row_dict.pop('mobile_number')
        return self.tel_process()

    def first_name_process(self):
        self.row_dict['name'] = self.row_dict.pop('first_name')
        return self.name_process()

    def ssn_process(self):
        """
        Предполагая, что валидный ssn имеет формат AAA-GG-SSSS и:
        - первые три цифры не могут быть 000, 666 или в диапазоне 900-999;
        - четвертая и пятая цифры должны быть в диапазоне от 01 до 99;
        - последние четыре цифры должны быть в диапазоне 0001 до 9999.
        """
        ssn = self.row_dict.get('ssn')[0]
        if re.fullmatch(
                r"(?!666|000|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}",
                ssn
        ):
            self.row_dict['user_additional_info'] += f"Номер SSN: {ssn}",
        else:
            self.logger.info(f"Bad ssn: {ssn}")
        self.row_dict['ssn'][1] = True

    def last_name_process(self):
        last_name = self.row_dict.get('last_name')[0]
        if re.fullmatch(r"[A-Z](?:[A-Za-z']+(?!'))", last_name):
            if len(self.row_dict.get('name')[0]) > 0 and self.row_dict['name'][1] is True:
                self.row_dict['user_fullname'] = f"{self.row_dict['name'][0]} {last_name}",
            else:
                self.row_dict['user_additional_info'] += f"Фамилия: {last_name}",
        else:
            self.logger.info(f"Bad last name: {last_name}")
        self.row_dict['last_name'][1] = True








