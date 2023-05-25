from pprint import pprint
from types import FunctionType
import inspect
from time import time
import os
import openpyxl
import datetime
import pandas as pd
import re

target_file = os.path.join('extracted_files', 'sql', 'data.sql')

with open(target_file, 'r') as file:
    sql_content = file.readlines()
first_line_values = re.search(r"\([a-z`\s,]+\)", sql_content[0])[0]
field_names = re.findall('`(\w+)`', first_line_values)
print(field_names)
print()
line_to_search = re.search(r"\(([\w,\s'.-@]+)\)", sql_content[1]).group(1)
print(line_to_search)
values = line_to_search.split(',\t')
print(values)
clean_values = [
    re.sub(r"'([\w,\s'.-@]+)'", r"\1", value) if isinstance(value, str) else value
    for value in values
]
print(clean_values)
print(len(clean_values))