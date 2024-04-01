import logging
from logging.handlers import RotatingFileHandler

log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_file_handler():
    file_handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=5)
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)
    return file_handler

def create_console_handler():
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.ERROR)
    return console_handler
