import logging
import inspect
from . import io_operations


class SupabaseHandler(logging.Handler):
    """Custom logging handler that sends logs to Supabase"""

    def emit(self, record):
        message = self.format(record)
        frame = inspect.currentframe().f_back.f_back
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        loc = f"File: {filename}, Line: {lineno}"
        io_operations.write_log(loc, message)


def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = SupabaseHandler()
    logger.addHandler(handler)
    return logger


def logger(message):
    logging.info(message)
