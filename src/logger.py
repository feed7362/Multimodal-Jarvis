import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os
import zipfile

class CustomLogger:
    LOG_DIR = "data/logs"
    SIZE_THRESHOLD = 1 * 1024 * 1024 * 1024  # 1 GB
    DAYS_THRESHOLD = 14  # Compress logs older than 14 day

    def __init__(self, name: str, to_console: bool = False):
        self.logger = None
        if not os.path.exists(self.LOG_DIR):
            os.makedirs(self.LOG_DIR)
        self.__setup_logger__(name, to_console)
        self.__compress_old_logs__(self.SIZE_THRESHOLD, self.DAYS_THRESHOLD)

    def __getattr__(self, attr):
        return getattr(self.logger, attr)

    def __setup_logger__(self, name: str, to_console: bool = False):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            log_filename = datetime.now().strftime("%Y-%m-%d") + "_app.log"
            log_file_path = os.path.join(self.LOG_DIR, log_filename)

            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

            if to_console:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)

            try:
                rotating_handler = RotatingFileHandler(
                    log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5
                )
                rotating_handler.setFormatter(formatter)
                self.logger.addHandler(rotating_handler)
            except Exception as e:
                self.logger.exception("Failed to create RotatingFileHandler: %s", e)

    def __compress_old_logs__(self, size_threshold: int, days_threshold: int):
        try:
            logs_files = [
                f for f in os.listdir(self.LOG_DIR)
                if os.path.isfile(os.path.join(self.LOG_DIR, f)) and f.endswith(".log")
            ]
            if not logs_files:
                self.logger.info("No log files found to process.")
                return

            files_size = sum(
                os.path.getsize(os.path.join(self.LOG_DIR, f)) for f in logs_files
            )
            oldest_file = min(
                logs_files, key=lambda f: os.path.getmtime(os.path.join(self.LOG_DIR, f))
            )
            file_days = (datetime.now().timestamp() - os.path.getmtime(os.path.join(self.LOG_DIR, oldest_file))) / 86400

            self.logger.info("Oldest log file %s is %.2f days old.", oldest_file, file_days)

            if files_size >= size_threshold and file_days >= days_threshold:
                zip_path = os.path.join(
                    self.LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_logs.zip"
                )
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=5) as zipf:
                    for f in logs_files:
                        full_path = os.path.join(self.LOG_DIR, f)
                        zipf.write(full_path, arcname=f)
                        self.logger.info("Added file to archive: %s", f)

                for f in logs_files:
                    try:
                        os.remove(os.path.join(self.LOG_DIR, f))
                        self.logger.info("Deleted log file: %s", f)
                    except Exception as e:
                        self.logger.exception("Failed to delete file %s: %s", f, e)

                self.logger.info("Archived log files to: %s", zip_path)
            else:
                self.logger.info(
                    "Skipping compression: size (%d/%d bytes), age (%.2f/%d days)",
                    files_size, size_threshold, file_days, days_threshold
                )
        except Exception as e:
            self.logger.exception("Error during log compression: %s", e)