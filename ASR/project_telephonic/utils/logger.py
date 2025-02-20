# project_telephonic/utils/logger.py
import logging

def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG for verbose output
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
