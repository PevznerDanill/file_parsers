import os
from time import time
import datetime
import pdfplumber
from pprint import pprint
from pdf_parser.p_parser import PdfParser


def main(target_file):
    start_time = time()

    with pdfplumber.open(target_file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            p_parser = PdfParser(table, chunks=7)
            p_parser.generate_csv()

    total_seconds = time() - start_time
    total_time_str = str(datetime.timedelta(seconds=total_seconds))
    print('Csv generated in', total_time_str)


if __name__ == '__main__':
    target_path = '../extracted_files/pdf/data_pdf.pdf'
    main(target_file=target_path)