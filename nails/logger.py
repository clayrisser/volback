from logging.handlers import RotatingFileHandler
from nails import get_config
import logging

def init_logger(app_name, app):
    app.log = logging.getLogger(app_name)
    level = logging.INFO
    if get_config(app_name, 'logger.level') == 'critical':
        level = logging.CRITICAL
    if get_config(app_name, 'logger.level') == 'error':
        level = logging.ERROR
    if get_config(app_name, 'logger.level') == 'warning':
        level = logging.WARNING
    if get_config('debug'):
        level = logging.DEBUG
    app.log.setLevel(level)
    if get_config(app_name, 'logger.file_handler'):
        file_handler = RotatingFileHandler(
            get_config(app_name, 'logger.file'),
            maxBytes=get_config(app_name, 'logger.max_bytes'),
            backupCount=get_config(app_name, 'logger.backup_count')
        )
        file_handler.setLevel(level)
        app.log.addHandler(file_handler)
    if get_config(app_name, 'logger.file_handler'):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        app.log.addHandler(stream_handler)
