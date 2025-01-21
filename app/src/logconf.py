import logging


def setup_logging():
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("app.log")

    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    loggers = {
        "llm": logging.DEBUG,
        "fetcher": logging.DEBUG,
    }

    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

        if not logger.hasHandlers():
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
