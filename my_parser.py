import csv
import logging
import re
import inspect
import os
from pprint import pprint
from typing import Dict, List, Union, Any, Optional, Tuple
from types import FunctionType
from datetime import datetime
from datetime import timedelta
from datetime import date
import itertools
import sys
from email_validator import validate_email, EmailNotValidError


class MyParser:
    """
    Основной класс MyParser, от которого наследуются три остальных парсер-класса.
    Здесь хранятся общие методы проверки данных, общие поля (для записи csv)
    и общие методы для записи данных в csv.

    Атрибуты:
        logger (logging.Logger): логгер для записи невалидных данных в локальный файл bad_values.log

        csv_path (str): названия файла, куда будут записываться итоговые данные. Изначально он лежит
        в папке каждого парсера и в нем уже заполнена шапка, что позволяет извлекать из него
        итоговые поля.

        date_formats_options (Tuple[Tuple[str]]): кортеж с возможными кодами форматов date

        symbols (Tuple[str]): кортеж с возможными символами разделяющие значения date

        start_date (datetime.date): дата 1 января 1970 для валидации поля date (должно быть не ранее этой даты)

        end_date (datetime.date): дата 31 декабря 2105 для валидации поля date (должно быть не позднее этой даты)

        row_dict (Dict): словарь для хранения пар поле-значение для каждой записи

        rows_to_write (Tuple): кортеж для хранения словарей с записями

        original_rows_list (Tuple): кортеж для хранения изначально собранной информации с файла

        date_formats (Tuple[str]): кортеж с данными возможных форматов date. Изначально содержит только
        формат года и заполняется методом get_date_formats, который прописывается
        при необходимости, то есть присутствия этого типа данных в файле.
    """
    logging.basicConfig(filename='bad_values.log', filemode='w',
                        format='%(asctime)s - %(message)s', level=logging.INFO)

    logger = logging.getLogger(__name__)

    csv_path = 'result.csv'

    date_formats_options = (
        ('%Y', '%d', '%b'),
        ('%Y', '%d', '%M'),
        ('%Y', '%b')
    )

    symbols = (' ', '-', '/')

    start_date = date(1970, 1, 1)

    end_date = date(2105, 12, 31)

    row_dict = {}

    file_fields = {}

    rows_to_write = ()

    original_rows_list = ()

    date_formats = ('%Y',)

    def __init__(self, chunks: Optional[int] = None) -> None:
        """
        Инициирует создание парсера. Аргумент chunks служит для ограничения записи данных за раз.
        Если он None, то все отфильтрованные данные сначала сохраняются в rows_to_write, а потом в
        конце записываются в csv. Иначе записывает chunks данных, сбрасывает rows_to_write и продолжает
        обработку остальных данных.

        Здесь же сохраняется список присутствующих в классе методов, который потом используется в методе
        func_map, определяющий, какие методы нужно запускать.

        И сохраняются итоговые поля из пустого файла csv с заполненной шапкой.
        """
        self.methods = [method[1] for method in inspect.getmembers(self, inspect.ismethod)]
        self.csv_fields = self.get_result_fields()
        self.func_map = self.update_func_map()
        self.chunks = chunks

    def get_result_fields(self) -> List[str]:
        """
        Открывает пустой итоговый файл с заполненной шапкой, чтобы посмотреть и сохранить его поля
        """
        if self.csv_path:
            with open(self.csv_path, 'r') as csv_file:
                reader = csv.reader(csv_file)
                return list(reader)[0]

    def get_date_formats(self) -> None:
        """
        Заполняет возможные комбинации форматов date. Прописывается при необходимости.
        """
        pass

    def update_dict(self, file_dict: Dict[str, Union[List[Union[str, bool]], Tuple[Union[str, bool]]]])\
            -> Dict[str, List[Union[str, bool]]]:
        """
        Заполняет словарь с row_dict. Метод прописан для идеального случая, когда все поля
        в парсируемом файле совпадают с необходимыми. Как правило метод перезаписывается,
        чтобы добавить остальные несовпадающие поля.
        Значения являются списком из двух элементов: самим значением и флагом, изначально
        переключенным на False. Когда данные проходят проверку, флаг ставится в значение True,
        чтобы проверяющий метод больше не трогал эти данные.
        """
        row_dict = {}
        for field_name, field_value in file_dict.items():
            if field_name.lower() in self.csv_fields:
                row_dict[field_name.lower()] = [str(field_value), False]
        if 'user_additional_info' not in row_dict:
            row_dict['user_additional_info'] = ()
        return row_dict

    def generate_csv(self) -> None:
        """
        Итерируется по кортежу собранных с файла данных и запускает их обработку.
        Если chunks не None, то записывает каждые chunks словарей из rows_to_write и сбрасывает его.
        Иначе просто после обработке записывает все.

        """
        if self.chunks:
            limit = 0
        else:
            limit = -1
        for ind, row_dict in enumerate(self.original_rows_list):
            self.row_dict = self.update_dict(row_dict)
            self.process_row_dict()
            if limit >= 0:
                limit += 1
                if limit == self.chunks:
                    self.write_rows()
                    print(f'Wrote {ind + 1} rows')
                    limit = 0
        if len(self.rows_to_write) > 0:
            print(f'Writing {len(self.rows_to_write)} rows')
            self.write_rows()
        print(f'Wrote all {ind + 1} rows')

    def write_rows(self) -> None:
        """
        Открывает итоговый csv файл и записывает туда обработанные данные, после чего
        сбрасывает кортеж rows_to_write.
        """
        with open(self.csv_path, 'a') as file:
            writer = csv.DictWriter(file, fieldnames=self.csv_fields)
            for data in self.rows_to_write:
                writer.writerow(data)
        self.rows_to_write = ()

    def update_func_map(self) -> Dict[str, FunctionType]:
        """
        Все функции, обрабатывающие данные, называются по паттерну поле_process.
        На основании этого метод генерирует и возвращает словарь с парами значений
        название поля - название функции для обработки этого поля
        """
        func_map = {
            re.sub(r"_process", "", method.__name__): method
            for method in self.methods if "_process" in method.__name__
        }

        return func_map

    def tel_process(self):
        """
        Обрабатывает телефонный номер (по формату США), предполагая, что должно быть 11 цифр (или 10 если без начальной единицы),
        которые могут быть разделены знаками "-" или пробелами. Первые три цифры (со второй по четвертую,
        если есть единица) могут быть в скобках.
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

    def date_process(self) -> None:
        """
        Обрабатывает дату из поля date.
        Исходя из документации ClickHouse, диапазон значений в этом поле
        [1970-01-01, 2149-06-06] и значение передается в формате %Y-%m-%d
        (https://clickhouse.com/docs/ru/sql-reference/data-types/date).
        В методе происходит попытка преобразовать строку в объект
        datetime и посмотреть, подходит ли он под диапазон.
        """
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

    def email_process(self) -> None:
        """
        Проверяет валидность email используя библиотеку email_validator. По умолчанию существование
        email не проверяется.
        """
        email = self.row_dict.get('email')[0]
        try:
            v = validate_email(email, check_deliverability=False)
            email = v["email"]

        except EmailNotValidError as e:
            self.logger.info(f"Bad email: {email}. {e}")
        finally:
            self.row_dict['email'][1] = True

    @classmethod
    def correct_number(cls, number: str) -> str:
        """
        Приводит валидное значение номера телефона к виду
        1 (000) 000 0000
        """
        digits = re.findall(r'\d', number)
        if len(digits) == 11:
            digits = digits[1:]
        return "1 ({}{}{}) {}{}{} {}{}{}{}".format(*digits)

    def zip_process(self) -> None:
        """
        Проверяет валидность zip-кода, предполагая что он должен состоять из пяти цифр и может быть
        дефиса и еще четырех цифр.
        """
        user_zip = self.row_dict.get('zip')[0]
        if not re.fullmatch(
            r"\d{5}(?:-\d{4})?", user_zip
        ):
            self.logger.info(f"Bad zip: {user_zip}")
            self.row_dict['zip'] = ("", True)
        else:
            self.row_dict['zip'][1] = True

    def address_process(self) -> None:
        """
        Проверяет валидность адреса, предполагая его следующие свойства:
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

    def user_fullname_process(self) -> None:
        """
        Проверяет валидность полного имени пользователя, предполагая что
        оно может состоять из одного или нескольких слов состоящих из латинских букв.
        Первое слово должно начинаться с заглавной буквы.
        Слова могут содержать точку (на случай сокращений) и апостроф.
        """
        full_name = self.row_dict.get('user_fullname')[0]
        if not re.fullmatch(
            r"(?:(?:[A-Z][A-z']*\.?)(?:(?:\s|-)[A-z']+\.?)*)(?<!\.)", full_name
        ):
            self.logger.info(f"Bad user_fullname: {full_name}")
            self.row_dict['user_fullname'] = ("", True)
        else:
            self.row_dict['user_fullname'][1] = True

    def name_process(self):
        """
        Проверяет валидность имени, предполагая что это одно слово из латинских букв, которое может начинаться на
        заглавную букву. Если слов больше двух, то данные переносятся на обработку в user_fullname_process.
        """
        name = self.row_dict.get('name')[0]
        if not re.fullmatch(r"[A-Z]?[a-z]+", name):
            self.logger.info(f"Bad name: {name}")
            self.row_dict['name'] = ("", True)
            if len(name.split()) > 1:
                if not self.row_dict.get('user_fullname'):
                    self.row_dict['user_fullname'] = [name, False]
                    self.user_fullname_process()
        else:
            self.row_dict['name'][1] = True

    def clean_row_dict(self, additional_info: str) -> None:
        """
        Чистит словарь с данными одной записи, подготавливая его к преобразованию csv.
        В частности, отсюда убираются списки [значение, bool] и остается только значение.
        Значение ключа user_additional_info переводится из кортежа, в которых
        собиралась дополнительная информация в переданную строку.
        """
        self.row_dict = {
            field_name: field_value[0]
            for field_name, field_value in self.row_dict.items()
            if field_name in self.csv_fields and field_name != 'user_additional_info'
        }
        self.row_dict['user_additional_info'] = additional_info

    def process_row_dict(self):
        """
        Вызывает обрабатывающие методы, если булевое значение в текущем поле в row_dict равно
        False. В каждом обрабатывающем методе после обработки флаг ставится на True.

        Также здесь генерируется строка user_additional_info.

        После row_dict добавляется в rows_to_write и сбрасывается.
        """
        for field_name, func in self.func_map.items():
            if field_name in self.row_dict.keys():
                if self.row_dict[field_name][1] is False:
                    func.__call__()

        additional_info = "|".join(self.row_dict['user_additional_info'])
        self.clean_row_dict(additional_info)
        self.rows_to_write += self.row_dict,
        self.row_dict = {}

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
        user_id = self.row_dict.get('user_ID')[0]
        if not re.fullmatch(
            r"\d+", user_id
        ):
            self.logger.info(f'Bad id: {user_id}')
            self.row_dict['user_ID'] = ("", True)
        else:
            self.row_dict['user_ID'][1] = True

    def username_process(self):
        username = self.row_dict.get('username')[0]
        if not re.fullmatch(
            r"(?:[\da-z_-]+)(?<!-)", username
        ):
            self.logger.info(f'Bad username: {username}')
            self.row_dict['username'] = ("", True)
        else:
            self.row_dict['username'][1] = True

    def dob_process(self):
        if len(self.date_formats) > 1:
            dob = self.row_dict.get('dob')[0]
            date_obj = None
            for date_format in self.date_formats:
                try:
                    date_obj = datetime.strptime(dob, date_format)
                    break
                except ValueError:
                    date_obj = None
            if not date_obj:
                self.row_dict['dob'] = ("", True)
                self.logger.info(f"Bad dob: {dob}")
            else:
                self.row_dict['dob'][1] = True

        else:
            print('Date formats are not configured')
            sys.exit(1)

