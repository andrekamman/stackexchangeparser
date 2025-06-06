from .core import (
    load_tables_config,
    setup_logging,
    find_subfolders_with_data,
    ensure_output_directory,
    get_table_files_in_folder,
    StackExchangeParserError,
    ConfigurationError,
    ValidationError
)
from .writers import CSVWriter, ParquetWriter

__version__ = "1.0.0"
__all__ = [
    "load_tables_config",
    "setup_logging", 
    "find_subfolders_with_data",
    "ensure_output_directory",
    "get_table_files_in_folder",
    "CSVWriter",
    "ParquetWriter",
    "process_stackexchange_data",
    "StackExchangeParserError",
    "ConfigurationError",
    "ValidationError"
]

def process_stackexchange_data(
    inputdir: str, 
    outputdir: str, 
    writer, 
    include_meta: bool = False, 
    config_path: str = None
) -> int:
    """
    Main processing function that handles the complete workflow.
    
    Args:
        inputdir: Input directory containing StackExchange XML files
        outputdir: Output directory for processed files
        writer: Writer instance (CSVWriter or ParquetWriter)
        include_meta: Whether to include meta sites
        config_path: Path to YAML config file (optional)
    
    Returns:
        Number of new directories created
    """
    import os
    import logging
    from datetime import datetime
    
    start_time = datetime.now()
    dircounter = 0
    
    # Load table configuration
    tables = load_tables_config(config_path)
    
    subfolders = find_subfolders_with_data(inputdir, tables, include_meta)
    
    logging.info("Input  folder: %s", inputdir)
    logging.info("Output folder: %s", outputdir)
    logging.info("Config file: %s", config_path or "default (config/tables.yaml)")
    
    if include_meta:
        logging.info("Including meta")
    else:
        logging.info("Skipping meta")
    
    for subfolder in subfolders:
        subfolder_name = os.path.basename(subfolder)
        
        if ensure_output_directory(outputdir, subfolder_name):
            dircounter += 1
            
            table_files = get_table_files_in_folder(subfolder, tables)
            
            for source_file, table_name, columns in table_files:
                file_extension = ".csv" if isinstance(writer, CSVWriter) else ".parquet"
                destination_file = os.path.join(outputdir, subfolder_name, f"{table_name}{file_extension}")
                writer.write_from_xml(source_file, table_name, columns, destination_file, subfolder_name)
    
    elapsed_time = datetime.now() - start_time
    logging.info("Finished processing, exported to %s new folders in %s", dircounter, elapsed_time)
    
    return dircounter