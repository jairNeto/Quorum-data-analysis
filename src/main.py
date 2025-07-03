#!/usr/bin/env python3
"""
Quorum Legislative Data Analysis
Main entry point for processing legislative voting data.
"""

import sys
import logging
from data_processor import DataProcessor

logger = logging.getLogger(__name__)


def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "/app/data"
    
    processor = DataProcessor(data_dir, "/app/output")
    
    logger.info("Starting legislative data processing")
    
    processor.generate_legislators_support_oppose_count()
    processor.generate_bills_csv()
    
    logger.info("Legislative data processing completed successfully")


if __name__ == '__main__':
    main() 