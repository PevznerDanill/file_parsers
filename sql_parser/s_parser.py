import csv
import logging
from my_parser import MyParser
import re
from pprint import pprint
from typing import List, Union
import itertools


class SqlParser(MyParser):
    """
    Парсер для sql dump файла, потомок MyParser. Так как он сломан, то просто парсит строку без
    использований библиотек для чтения sql.
    """

    def __init__(self, sql_content: str, chunks=None) -> None:
        """
        Перед родительским, сохраняет строку из sql dump, создает словарь из записей и запускает формирование
        возможных форматов дат.
        """
        self.sql_content = sql_content
        self.generate_dict()
        self.get_date_formats()
        super().__init__(chunks=chunks)

    def get_date_formats(self) -> None:
        """
        Создает кортеж с возможными форматами дат, используя itertools.permutations.
        """
        for new_format in self.date_formats_options:
            permutations = itertools.permutations(new_format)
            for perm in permutations:
                for symbol in self.symbols:
                    self.date_formats += f"{symbol}".join(perm),

    def sex_process(self):
        """
        Проверяет на валидность данные поля sex и, если валидно, добавляет к user_additional_info.
        """
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
        """
        Меняет название полей userid на user_ID и birth на dob
        """
        if field_name == 'userid':
            return re.sub(r'id', '_ID', field_name)
        if field_name == 'birth':
            return 'dob'
        return field_name

    def update_dict(self, file_dict):
        """
        Добавляет дополнительные поля.
        """
        row_dict = super().update_dict(file_dict)
        row_dict.update(file_dict)
        return row_dict

    def generate_dict(self):
        """
        Собирает данные из дампа и сохраняет в виде словаря в кортеж original_rows_list.
        """
        all_lines = re.finditer(
            r"\((.+)\)", self.sql_content
        )
        for ind, line in enumerate(all_lines):
            if ind == 0:
                field_names = [
                    self.change_field_names(field_name)
                    for field_name in re.findall('`(\w+)`', line.group(1))
                    if field_name != 'mobile'
                ]

            elif not re.search(r"INSERT INTO", line.group(1)):
                values = (
                    [re.sub(r"'(.+)'", r"\1", value), False]
                    for value in line.group(1).split(',\t')
                )

                self.original_rows_list += dict(zip(field_names, values)),

    def password_process(self):
        """
        Сохраняет хэш пароля в user_additional_info.
        Конечно, можно было бы добавить проверку с паттерном типа
        r"[\da-z]{16,72}", так как это подходило бы популярным алгоритмам хэширования, но
        все-таки такой алгоритм можно написать и самому и, следовательно, подобный фильтр
        пропустил бы потенциально валидный хеш с кустарным алгоритмом.

        """
        password = self.row_dict.get('password')[0]
        self.row_dict['user_additional_info'] += f'Хэш пароля: {password}',
        self.row_dict['password'][1] = True





