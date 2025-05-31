import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os
import zipfile

class CustomLogger:
    LOG_DIR = "data/logs"
    SIZE_THRESHOLD = 1 * 1024 * 1024 * 1024
    DAYS_THRESHOLD = None
    def __init__(self, name: str, to_console: bool = False):
        self.logger = None
        if not os.path.exists(self.LOG_DIR):
            os.makedirs(self.LOG_DIR)    
        self.__setup_logger__(name, to_console)
        self.__compress_old_logs__(self.SIZE_THRESHOLD, self.DAYS_THRESHOLD)
        
    def __getattr__(self, attr):
        return getattr(self.logger, attr)
    
    def __setup_logger__(self, name: str, to_console: bool = False) -> logging.Logger:
        """
        Setup logger with the given name and predefined configurations.
        """
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
                rotating_handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5)
                rotating_handler.setFormatter(formatter)
                self.logger.addHandler(rotating_handler)

            except Exception as e:
                self.logger.exception("Error during creating RotatingFileHandler: %s", e)
    
    def __compress_old_logs__(self, size_threshold: int = None, days_threshold: int = None):
        """
        Compress log files older than the specified number of days into a ZIP file,
        and then delete the original log files.
        """
        if size_threshold is None:
            size_threshold = self.SIZE_THRESHOLD
        if days_threshold is None:
            days_threshold = self.DAYS_THRESHOLD

        self.logger = logging.getLogger("compress_old_logs")
        try:
            logs_files = [f for f in os.listdir(self.LOG_DIR) if os.path.isfile(os.path.join(self.LOG_DIR, f)) and f.endswith(".log")]
            if not logs_files:
                self.logger.info("No log files found to process.")
                return
            files_size = 0
            oldest_file = min(logs_files, key=lambda f: os.path.getmtime(os.path.join(self.LOG_DIR, f)))
            file_days = (datetime.now().timestamp() - os.path.getmtime(os.path.join(self.LOG_DIR, oldest_file))) / 86400
            self.logger.info(f"Oldest log file {oldest_file} is {file_days:.2f} days old.")
            
            for file in logs_files:
                files_size += os.path.getsize(os.path.join(self.LOG_DIR, file))
                
            if files_size >= size_threshold and file_days >= days_threshold:
                zip_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_app.ZIP"
                with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED, compresslevel=5) as ZIP: # compress level[0-9]
                    for file in logs_files:
                        try:
                            if os.path.join(self.LOG_DIR, file):
                                ZIP.write(os.path.join(self.LOG_DIR, file), os.path.basename(file))
                                self.logger.info("Added file to archive: %s", file)
                        except Exception as e:
                            self.logger.exception("Error while adding %s to archive: %s", file, e)
                            
                for file_path in logs_files:
                    try:
                        os.remove(os.path.join(self.LOG_DIR, file_path))
                        self.logger.info("Deleted log file: %s", file_path)
                    except Exception as e:
                        self.logger.exception("Error while deleting file %s: %s", file_path, e)
                self.logger.info("All log files added to archives : %s", zip_filename)
            else:
                self.logger.info("Conditions for compressing not satisfied (require %d bytes, found %d bytes or days %d isn`t %d).",
                            size_threshold, files_size, file_days, days_threshold)
        except Exception as e:
            self.logger.exception("Error during making archive RotatingFileHandler: %s", e)
            self.logger.exception("Error during making archive RotatingFileHandler: %s", e)