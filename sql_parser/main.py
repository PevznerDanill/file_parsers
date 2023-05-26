import os
from time import time
import datetime
from sql_parser.s_parser import SqlParser

def main(target_file):
    start_time = time()

    with open(target_file, 'r') as sql_file:
        sql_content = sql_file.read()
        sql_parser = SqlParser(sql_content, chunks=5000)

    sql_parser.generate_csv()

    total_seconds = time() - start_time
    total_time_str = str(datetime.timedelta(seconds=total_seconds))
    print('Csv generated in', total_time_str)


if __name__ == '__main__':
    target_path = '../extracted_files/sql/data.sql'
    main(target_file=target_path)