import logging


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger: logging.Logger, log_level=logging.INFO):
        self.logger: logging.Logger = logger
        self.log_level = log_level

    def write(self, message):
        if isinstance(message, bytes):  # Handle bytes (if necessary, for stderr)
            message = message.decode("utf-8")

        for line in message.splitlines():
            stripped_line = line.strip()
            if stripped_line != '':
                self.logger.log(self.log_level, stripped_line)

    def flush(self):
        pass
