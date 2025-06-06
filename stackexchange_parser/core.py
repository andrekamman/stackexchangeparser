from lxml import etree
from pathlib import Path
import os
import logging
import yaml
from typing import Dict, List, Optional, Tuple, Iterator, Callable, Any, Union

class StackExchangeParserError(Exception):
    """Base exception for StackExchange parser errors."""
    pass

class ConfigurationError(StackExchangeParserError):
    """Raised when configuration file is invalid or missing."""
    pass

class ValidationError(StackExchangeParserError):
    """Raised when input validation fails."""
    pass

def load_tables_config(config_path: Optional[str] = None) -> Dict[str, List[str]]:
    """Load table configuration from YAML file with validation."""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "tables.yaml")
    
    # Validate config file exists
    if not os.path.isfile(config_path):
        raise ConfigurationError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML format in {config_path}: {e}")
    except Exception as e:
        raise ConfigurationError(f"Error reading configuration file {config_path}: {e}")
    
    # Validate config structure
    if not isinstance(config, dict):
        raise ConfigurationError(f"Configuration file must contain a dictionary, got {type(config)}")
    
    if 'tables' not in config:
        raise ConfigurationError("Configuration file must contain a 'tables' section")
    
    tables = config['tables']
    if not isinstance(tables, dict):
        raise ConfigurationError("'tables' section must be a dictionary")
    
    # Validate each table configuration
    for table_name, columns in tables.items():
        if not isinstance(columns, list):
            raise ConfigurationError(f"Table '{table_name}' must have a list of columns, got {type(columns)}")
        if not columns:
            raise ConfigurationError(f"Table '{table_name}' must have at least one column")
        if not all(isinstance(col, str) for col in columns):
            raise ConfigurationError(f"All columns in table '{table_name}' must be strings")
    
    return tables

def get_stackexchange_files(tables: Dict[str, List[str]]) -> List[str]:
    """Generate list of expected XML files from table configuration."""
    return [f"{table}.xml" for table in tables]

def fast_scandir(dirname: str) -> List[str]:
    """Recursively scan directory for subdirectories with error handling."""
    if not os.path.isdir(dirname):
        raise ValidationError(f"Directory does not exist: {dirname}")
    
    try:
        subfolders = [f.path for f in os.scandir(dirname) if f.is_dir()]
        for subdir in list(subfolders):
            try:
                subfolders.extend(fast_scandir(subdir))
            except PermissionError:
                logging.warning(f"Permission denied accessing directory: {subdir}")
                continue
        return subfolders
    except PermissionError:
        raise ValidationError(f"Permission denied accessing directory: {dirname}")
    except Exception as e:
        raise ValidationError(f"Error scanning directory {dirname}: {e}")

def has_validfiles(dirname: str, validfiles: List[str]) -> bool:
    """Check if directory contains any valid StackExchange files."""
    try:
        files = [f.name for f in os.scandir(dirname) if not f.is_dir()]
        return any(file in validfiles for file in files)
    except PermissionError:
        logging.warning(f"Permission denied accessing directory: {dirname}")
        return False
    except Exception as e:
        logging.warning(f"Error checking files in directory {dirname}: {e}")
        return False

def transform_column(column: Any) -> Union[int, str]:
    """Transform XML column value, handling boolean conversion and escaping."""
    if str(column) == "False":
        return 0
    elif str(column) == "True":
        return 1
    else:
        return column.replace("\r\n","&#xD;&#xA;").replace("\r","&#xD;").replace("\n", "&#xA;")

def parse_xml_rows(
    sourcefilename: str, 
    columns: List[str], 
    progress_callback: Optional[Callable[[int], None]] = None
) -> Iterator[List[Union[int, str, None]]]:
    """Parse XML file and yield rows with error handling."""
    if not os.path.isfile(sourcefilename):
        raise ValidationError(f"Source file does not exist: {sourcefilename}")
    
    try:
        context = etree.iterparse(sourcefilename, events=('end',), tag='row')
        rowcounter = 0
        
        for event, element in context:
            rowcounter += 1
            if progress_callback:
                progress_callback(rowcounter)
            
            row = [transform_column(element.attrib[column]) if column in element.attrib else None for column in columns]
            yield row
            
            while element.getprevious() is not None:
                del element.getparent()[0]
                
    except etree.XMLSyntaxError as e:
        raise ValidationError(f"Invalid XML in file {sourcefilename}: {e}")
    except Exception as e:
        raise ValidationError(f"Error parsing XML file {sourcefilename}: {e}")

def setup_logging() -> None:
    """Configure logging with timestamp format."""
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

def find_subfolders_with_data(
    inputdir: str, 
    tables: Dict[str, List[str]], 
    include_meta: bool = False
) -> List[str]:
    """Find subfolders containing StackExchange data files."""
    if not os.path.isdir(inputdir):
        raise ValidationError(f"Input directory does not exist: {inputdir}")
    
    stackexchangefiles = get_stackexchange_files(tables)
    subfolders = fast_scandir(inputdir)
    
    if has_validfiles(inputdir, stackexchangefiles):
        subfolders.append(inputdir)
    
    valid_subfolders = []
    for subfolder in subfolders:
        if not include_meta:
            if ".meta." in os.path.basename(subfolder) or os.path.basename(subfolder).startswith("meta."):
                continue
        if has_validfiles(subfolder, stackexchangefiles):
            valid_subfolders.append(subfolder)
    
    if not valid_subfolders:
        logging.warning(f"No StackExchange data files found in {inputdir}")
    
    return valid_subfolders

def ensure_output_directory(outputdir: str, subfolder_name: str) -> bool:
    """Ensure output directory exists, creating it if necessary."""
    # Validate parent output directory exists
    if not os.path.isdir(outputdir):
        try:
            os.makedirs(outputdir, exist_ok=True)
        except Exception as e:
            raise ValidationError(f"Cannot create output directory {outputdir}: {e}")
    
    output_path = os.path.join(outputdir, subfolder_name)
    if not os.path.isdir(output_path):
        try:
            os.mkdir(output_path)
            return True
        except Exception as e:
            raise ValidationError(f"Cannot create subdirectory {output_path}: {e}")
    return False

def get_table_files_in_folder(
    subfolder: str, 
    tables: Dict[str, List[str]]
) -> List[Tuple[str, str, List[str]]]:
    """Get list of table files found in folder with their metadata."""
    stackexchangefiles = get_stackexchange_files(tables)
    found_files = []
    
    for file in stackexchangefiles:
        file_path = os.path.join(subfolder, file)
        if os.path.isfile(file_path):
            table_name = Path(file).stem
            found_files.append((file_path, table_name, tables[table_name]))
    
    return found_files