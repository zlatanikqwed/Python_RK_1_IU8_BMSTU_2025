"""
@brief Centralized logger configuration for R&D Department Analysis
Provides unified logging functionality with file handlers.
"""

import logging
import os
from datetime import datetime


class AnalysisLogger:
    """
    @brief Custom logger class for R&D analysis operations.
    Handles creation of log directory, log files, and format configuration.
    """

    def __init__(self, log_directory="logs"):
        """
        @brief Initialize analysis logger.
        Creates log directory (if missing) and sets up base format for all loggers.
        @param log_directory.
        """
        self.log_directory = log_directory
        self._ensure_directory()
        self._configure_root_logger()

    def _ensure_directory(self):
        """
        @brief Check and create log directory if it doesn't exist.
        Ensures consistent structure for storing daily logs.
        @throws OSError if the directory cannot be created.
        """
        try:
            if not os.path.exists(self.log_directory):
                os.makedirs(self.log_directory)
        except Exception as error:
            print(f"Cannot create directory: {error}")

    def _configure_root_logger(self):
        """
        @brief Configure the root logger with a standard format and INFO level.
        Called once on initialization to avoid duplicated handlers.
        """
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def get_logger(self, analysis_name):
        """
        @brief Create and configure a dedicated logger for a specific analysis module.
        @param name Logical name of the analyzer.
        @return Configured logging.Logger instance.
        """
        logger = logging.getLogger(analysis_name)
        logger.setLevel(logging.INFO)

        # Remove old handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        log_filename = f"{analysis_name.lower()}_{datetime.now().strftime('%Y%m%d')}.log"
        log_path = os.path.join(self.log_directory, log_filename)

        try:
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as error:
            print(f"Cannot create file handler for: {error}")

        return logger


# Global logger instance 
analysis_logger = AnalysisLogger()
