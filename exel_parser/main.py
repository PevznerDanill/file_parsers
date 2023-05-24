import os
from time import time
import openpyxl
from openpyxl.reader import workbook
from openpyxl.worksheet.worksheet import Worksheet
from exel_parser.e_parser import ExcelParser
import datetime


def main(target_file):
    start_time = time()

    work_book: workbook = openpyxl.load_workbook(target_file)

    worksheet: Worksheet = work_book.active
    e_parser = ExcelParser(worksheet)
    print('Starting to process', worksheet.max_row, 'rows')
    e_parser.generate_csv()
    total_seconds = time() - start_time
    total_time_str = str(datetime.timedelta(seconds=total_seconds))
    print('Csv generated in', total_time_str)


if __name__ == '__main__':
    file_to_parse = os.path.abspath(os.path.join('..', 'extracted_files', 'excel', 'data.xlsx'))
    main(target_file=file_to_parse)
