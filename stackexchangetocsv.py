#!/usr/bin/env python3
"""
DEPRECATED: Use stackexchange_convert.py instead

This script is kept for backwards compatibility.
For new projects, use: python stackexchange_convert.py -f csv
"""

import argparse
from stackexchange_parser import setup_logging, process_stackexchange_data, CSVWriter

def main():
    parser = argparse.ArgumentParser(
        description="Convert StackExchange XML to CSV (DEPRECATED: use stackexchange_convert.py)"
    )
    parser.add_argument("inputfolder", help="Location of the StackExchange files or subfolders")
    parser.add_argument("outputfolder", help="Export destination folder where subfolders will be created")
    parser.add_argument("-m", "--meta", help="Also export the meta files", action="store_true")
    parser.add_argument("-p", "--progressindicatorvalue", help="Shows nr of rows imported for larger files", type=int, default=10000000)
    parser.add_argument("-c", "--config", help="Path to YAML config file with table definitions", type=str, default=None)
    args = parser.parse_args()

    setup_logging()
    
    writer = CSVWriter(progress_indicator_value=args.progressindicatorvalue)
    process_stackexchange_data(args.inputfolder, args.outputfolder, writer, args.meta, args.config)

if __name__ == "__main__":
    main()

