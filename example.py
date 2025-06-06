#!/usr/bin/env python3
"""
StackExchange Parser - Usage Examples

This file demonstrates various ways to use the StackExchange Parser library
for converting XML dumps from StackExchange sites to CSV or Parquet format.

Example data structure expected:
input_folder/
├── stackoverflow.com/
│   ├── Posts.xml
│   ├── Users.xml
│   ├── Comments.xml
│   └── ...
├── meta.stackoverflow.com/
│   ├── Posts.xml
│   └── ...
└── serverfault.com/
    ├── Posts.xml
    └── ...
"""

import os
import logging
from stackexchange_parser import (
    process_stackexchange_data,
    CSVWriter,
    ParquetWriter,
    load_tables_config,
    setup_logging
)


def example_basic_csv_conversion():
    """
    Example 1: Basic CSV conversion
    
    Converts all StackExchange XML files in input directory to CSV format.
    """
    print("Example 1: Basic CSV conversion")
    
    # Setup logging to see progress
    setup_logging()
    
    # Create CSV writer
    writer = CSVWriter()
    
    # Process the data
    input_dir = "data/stackexchange_dumps"
    output_dir = "output/csv_files"
    
    try:
        new_folders = process_stackexchange_data(
            inputdir=input_dir,
            outputdir=output_dir,
            writer=writer
        )
        print(f"Successfully created {new_folders} new folders with CSV files")
    except Exception as e:
        print(f"Error during processing: {e}")


def example_parquet_with_options():
    """
    Example 2: Parquet conversion with custom options
    
    Demonstrates using ParquetWriter with custom batch size and including meta sites.
    """
    print("\nExample 2: Parquet conversion with custom options")
    
    setup_logging()
    
    # Create Parquet writer with custom batch size (500K rows per file)
    writer = ParquetWriter(
        batch_size=500000,
        progress_indicator_value=100000  # Show progress every 100K rows
    )
    
    input_dir = "data/stackexchange_dumps"
    output_dir = "output/parquet_files"
    
    try:
        new_folders = process_stackexchange_data(
            inputdir=input_dir,
            outputdir=output_dir,
            writer=writer,
            include_meta=True  # Include meta sites like meta.stackoverflow.com
        )
        print(f"Successfully created {new_folders} new folders with Parquet files")
    except Exception as e:
        print(f"Error during processing: {e}")


def example_custom_configuration():
    """
    Example 3: Using custom table configuration
    
    Shows how to use a custom YAML configuration file to control
    which columns are extracted from each table.
    """
    print("\nExample 3: Custom table configuration")
    
    # First, let's examine the default configuration
    try:
        default_tables = load_tables_config()
        print("Default tables available:")
        for table_name, columns in default_tables.items():
            print(f"  {table_name}: {len(columns)} columns")
            print(f"    First 5 columns: {columns[:5]}")
    except Exception as e:
        print(f"Error loading default config: {e}")
        return
    
    # Create a custom configuration file
    custom_config_content = """
tables:
  Posts:
    - Id
    - PostTypeId
    - CreationDate
    - Score
    - Title
    - Body
    - OwnerUserId
    - Tags
  Users:
    - Id
    - DisplayName
    - CreationDate
    - Reputation
    - Location
  Comments:
    - Id
    - PostId
    - UserId
    - CreationDate
    - Text
"""
    
    custom_config_path = "custom_tables.yaml"
    
    # Write custom configuration
    try:
        with open(custom_config_path, 'w') as f:
            f.write(custom_config_content)
        print(f"Created custom configuration: {custom_config_path}")
        
        # Load and validate custom configuration
        custom_tables = load_tables_config(custom_config_path)
        print("Custom tables loaded:")
        for table_name, columns in custom_tables.items():
            print(f"  {table_name}: {columns}")
        
        # Use custom configuration for processing
        setup_logging()
        writer = CSVWriter()
        
        new_folders = process_stackexchange_data(
            inputdir="data/stackexchange_dumps",
            outputdir="output/custom_csv",
            writer=writer,
            config_path=custom_config_path
        )
        print(f"Processed with custom config: {new_folders} folders created")
        
    except Exception as e:
        print(f"Error with custom configuration: {e}")
    finally:
        # Clean up
        if os.path.exists(custom_config_path):
            os.remove(custom_config_path)


def example_error_handling():
    """
    Example 4: Proper error handling
    
    Demonstrates how to handle various types of errors that might occur.
    """
    print("\nExample 4: Error handling demonstration")
    
    from stackexchange_parser import StackExchangeParserError, ConfigurationError, ValidationError
    
    setup_logging()
    
    # Example of handling missing input directory
    try:
        writer = CSVWriter()
        process_stackexchange_data(
            inputdir="nonexistent_directory",
            outputdir="output/test",
            writer=writer
        )
    except FileNotFoundError as e:
        print(f"Handled missing input directory: {e}")
    except StackExchangeParserError as e:
        print(f"Handled parser error: {e}")
    
    # Example of handling invalid configuration
    try:
        invalid_config = "nonexistent_config.yaml"
        load_tables_config(invalid_config)
    except ConfigurationError as e:
        print(f"Handled configuration error: {e}")
    except FileNotFoundError as e:
        print(f"Handled missing config file: {e}")


def example_memory_efficient_processing():
    """
    Example 5: Memory-efficient processing for large datasets
    
    Shows best practices for processing very large StackExchange dumps.
    """
    print("\nExample 5: Memory-efficient processing")
    
    setup_logging()
    
    # For very large datasets, use smaller batch sizes
    writer = ParquetWriter(
        batch_size=100000,  # Smaller batches for lower memory usage
        progress_indicator_value=50000  # More frequent progress updates
    )
    
    input_dir = "data/large_stackexchange_dumps"
    output_dir = "output/large_parquet"
    
    try:
        # Monitor memory usage during processing
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"Initial memory usage: {initial_memory:.1f} MB")
        
        new_folders = process_stackexchange_data(
            inputdir=input_dir,
            outputdir=output_dir,
            writer=writer
        )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Final memory usage: {final_memory:.1f} MB")
        print(f"Memory increase: {final_memory - initial_memory:.1f} MB")
        print(f"Processed {new_folders} folders")
        
    except ImportError:
        print("psutil not available for memory monitoring")
        # Process without memory monitoring
        try:
            new_folders = process_stackexchange_data(
                inputdir=input_dir,
                outputdir=output_dir,
                writer=writer
            )
            print(f"Processed {new_folders} folders")
        except Exception as e:
            print(f"Error during processing: {e}")
    except Exception as e:
        print(f"Error during processing: {e}")


def example_inspect_data_before_processing():
    """
    Example 6: Inspecting data structure before processing
    
    Shows how to examine what data is available before starting conversion.
    """
    print("\nExample 6: Data inspection")
    
    from stackexchange_parser import find_subfolders_with_data, get_table_files_in_folder
    
    input_dir = "data/stackexchange_dumps"
    
    try:
        # Load configuration
        tables = load_tables_config()
        
        # Find all subfolders with StackExchange data
        subfolders = find_subfolders_with_data(input_dir, tables, include_meta=True)
        
        print(f"Found {len(subfolders)} StackExchange sites:")
        
        for subfolder in subfolders:
            site_name = os.path.basename(subfolder)
            print(f"\n  Site: {site_name}")
            
            # Get table files in this folder
            table_files = get_table_files_in_folder(subfolder, tables)
            
            for source_file, table_name, columns in table_files:
                file_size = os.path.getsize(source_file) / (1024 * 1024)  # MB
                print(f"    {table_name}: {file_size:.1f} MB ({len(columns)} columns)")
        
        if not subfolders:
            print("No StackExchange data found. Make sure your input directory contains")
            print("subdirectories with XML files like Posts.xml, Users.xml, etc.")
            
    except Exception as e:
        print(f"Error during inspection: {e}")


if __name__ == "__main__":
    """
    Run all examples. Modify the paths and uncomment examples as needed.
    
    Before running:
    1. Install requirements: pip install -r requirements.txt
    2. Download StackExchange data dump from https://archive.org/details/stackexchange
    3. Extract to a directory structure like described at the top of this file
    4. Update the input_dir paths in the examples above
    """
    
    print("StackExchange Parser - Usage Examples")
    print("=" * 50)
    
    # Note: These examples use placeholder paths. 
    # Update the paths to match your actual data location.
    
    print("\nNOTE: Update the input directory paths in this file before running!")
    print("Download StackExchange dumps from: https://archive.org/details/stackexchange")
    print()
    
    # Uncomment the examples you want to run:
    
    # example_basic_csv_conversion()
    # example_parquet_with_options()
    # example_custom_configuration()
    # example_error_handling()
    # example_memory_efficient_processing()
    # example_inspect_data_before_processing()
    
    # Simple test with current directory structure
    example_inspect_data_before_processing()