import re
import csv


with open('bl_struct.txt', 'r') as file:
    opened_file = file.read()


csv_fields = re.findall(
        r"`(\w+)`", opened_file
)

with open('exel_parser/result.csv', 'w') as result_file:
    result_writer = csv.writer(result_file, delimiter=',', quotechar='"')
    result_writer.writerow(csv_fields)

