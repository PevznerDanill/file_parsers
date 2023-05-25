import os
from time import time
from exel_parser.e_parser import ExcelParser
import datetime
import pandas


def main(target_file):
    start_time = time()

    data_frame = pandas.read_excel(target_file)
    e_parser = ExcelParser(data_frame=data_frame, chunks=553)
    e_parser.generate_csv()
    total_seconds = time() - start_time
    total_time_str = str(datetime.timedelta(seconds=total_seconds))
    print('Csv generated in', total_time_str)


if __name__ == '__main__':
    file_to_parse = os.path.abspath(os.path.join('..', 'extracted_files', 'excel', 'data.xlsx'))
    main(target_file=file_to_parse)
