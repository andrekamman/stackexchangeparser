#!/usr/bin/env python3
"""
StackExchange XML to CSV/Parquet Converter

This is the main CLI entry point for converting StackExchange XML dumps
to CSV or Parquet format.
"""

from stackexchange_parser.cli import main

if __name__ == "__main__":
    main()