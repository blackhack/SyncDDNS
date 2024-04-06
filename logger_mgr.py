#    Copyright 2024 JDavid(Blackhack) <davidaristi.0504@gmail.com>

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
logger_path = os.path.join(script_dir, "console.log")

# Create handlers for writing to file and printing to console
file_handler = logging.FileHandler(logger_path, "w")
console_handler = logging.StreamHandler()
# Create a formatter and set it for both handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# INFO by default, but can be set in the config
default_log_level = "INFO"
loggers = []


def initialize_logger(name: str):
    """Initialize and configure the logger."""

    logger = logging.getLogger(name)
    logger.setLevel(default_log_level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    loggers.append(logger)

    return logger


def set_log_level(level: str):
    global default_log_level
    default_log_level = level

    for logger in loggers:
        logger.setLevel(level)
