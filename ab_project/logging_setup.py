import logging

from ab_project.config.config import app_config


def initialize_logging():
    log_formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(filename)-20.20s] [%(funcName)-30.30s]"
        "[l %(lineno)-4.4s] [%(levelname)-7.7s]\t%(message)s"
    )
    root_logger = logging.getLogger()

    log_filepath = f"{app_config.logging.log_path}/{app_config.logging.log_filename}.log"
    with open(log_filepath, "r") as log_file:
        log_history = sum(1 for _ in log_file)

    if log_history > int(app_config.logging.max_history):
        with open(log_filepath, "w") as _:
            msg = f"Log file was cleaned (history > {app_config.logging.max_history})."
    elif log_history > 0.8 * int(app_config.logging.max_history):
        msg = f"You've reached 80% of logging max history ({log_history} lines). Log file may be cleared soon."
    else:
        msg = None

    file_handler = logging.FileHandler(log_filepath)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)

    root_logger.setLevel(getattr(logging, app_config.logging.level))

    if msg is not None:
        root_logger.warning(msg)
