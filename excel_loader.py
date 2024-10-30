import openpyxl
import logging

def load_excel(file_name):
    try:
        workbook = openpyxl.load_workbook(file_name)
        logging.info(f'Файл {file_name} успешно загружен.')
        return workbook.active  # Возвращаем активный лист
    except FileNotFoundError:
        logging.error(f'Файл {file_name} не найден.')
        raise
