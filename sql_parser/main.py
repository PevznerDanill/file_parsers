import os
from time import time
import datetime
from sql_parser.s_parser import SqlParser

def main(target_file):
    start_time = time()

    with open(target_file, 'r') as sql_file:
        sql_content = sql_file.readlines()
        sql_parser = SqlParser(sql_content)

    sql_parser.show_dict()

    total_seconds = time() - start_time
    total_time_str = str(datetime.timedelta(seconds=total_seconds))
    print('Csv generated in', total_time_str)


if __name__ == '__main__':
    target_path = '../extracted_files/sql/data.sql'
    main(target_file=target_path)