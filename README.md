# Парсеры для Blitz Project - Test Task

## Всего три парсера: 

* Парсер для excel в папке excel_parser
* Парсер для pdf в папке pdf_parser
* Парсер для sql в папке sql_parser

В каждой из этих папок лежит main.py, запуск которого запускает скрипт.
Парсеры унаследованны от my_parser.py в корневой папке. В нем расписана логика работы
всех парсеров.

* excel_parser использует для чтения pandas.
* pdf_parser использует pdfplumber
* sql_parser ипспользует только re, так как dump сломан





