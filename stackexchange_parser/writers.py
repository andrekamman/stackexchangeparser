import csv
import os
import logging
from abc import ABC, abstractmethod
from typing import List, Union
from .core import parse_xml_rows, ValidationError

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

class BaseWriter(ABC):
    def __init__(self, progress_indicator_value: int = 10000000) -> None:
        self.progress_indicator_value = progress_indicator_value
    
    @abstractmethod
    def write_from_xml(
        self, 
        sourcefilename: str, 
        table: str, 
        columns: List[str], 
        destinationfilename: str, 
        subfolder_name: str
    ) -> None:
        pass
    
    def _create_progress_callback(self, table: str, subfolder_name: str):
        def progress_callback(rowcounter: int) -> None:
            if (rowcounter % self.progress_indicator_value == 0):
                logging.info("            Exported %s rows for %s in %s", rowcounter, table, subfolder_name)
        return progress_callback

class CSVWriter(BaseWriter):
    def write_from_xml(
        self, 
        sourcefilename: str, 
        table: str, 
        columns: List[str], 
        destinationfilename: str, 
        subfolder_name: str
    ) -> None:
        logging.info("Exporting:  %s - %s.csv", subfolder_name, table)
        
        progress_callback = self._create_progress_callback(table, subfolder_name)
        
        # Validate destination directory exists
        dest_dir = os.path.dirname(destinationfilename)
        if dest_dir and not os.path.isdir(dest_dir):
            raise ValidationError(f"Destination directory does not exist: {dest_dir}")
        
        try:
            with open(destinationfilename, 'w', newline='', encoding="utf-8") as f:
                writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                writer.writerow(columns)
                
                for row in parse_xml_rows(sourcefilename, columns, progress_callback):
                    # Convert None to empty string for CSV compatibility
                    csv_row = ['' if cell is None else cell for cell in row]
                    writer.writerow(csv_row)
        except PermissionError:
            raise ValidationError(f"Permission denied writing to file: {destinationfilename}")
        except Exception as e:
            raise ValidationError(f"Error writing CSV file {destinationfilename}: {e}")

class ParquetWriter(BaseWriter):
    def __init__(self, progress_indicator_value: int = 10000000, batch_size: int = 1000000) -> None:
        super().__init__(progress_indicator_value)
        
        if batch_size <= 0:
            raise ValueError("Batch size must be greater than 0")
        self.batch_size = batch_size
        
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas and pyarrow are required for Parquet output. Install with: pip install pandas pyarrow")
        
        # Check if pyarrow is available
        try:
            import pyarrow
        except ImportError:
            raise ImportError("pyarrow is required for Parquet output. Install with: pip install pyarrow")
    
    def write_from_xml(
        self, 
        sourcefilename: str, 
        table: str, 
        columns: List[str], 
        destinationfilename: str, 
        subfolder_name: str
    ) -> None:
        logging.info("Exporting:  %s - %s.parquet (batch size: %s)", subfolder_name, table, self.batch_size)
        
        # Validate destination directory exists
        dest_dir = os.path.dirname(destinationfilename)
        if dest_dir and not os.path.isdir(dest_dir):
            raise ValidationError(f"Destination directory does not exist: {dest_dir}")
        
        progress_callback = self._create_progress_callback(table, subfolder_name)
        
        batch_data = []
        filenumber = 1
        
        for row in parse_xml_rows(sourcefilename, columns, progress_callback):
            batch_data.append(row)
            
            if len(batch_data) >= self.batch_size:
                self._write_batch(batch_data, columns, destinationfilename, filenumber, subfolder_name)
                batch_data = []
                filenumber += 1
        
        if batch_data:
            self._write_final_batch(batch_data, columns, destinationfilename, filenumber, subfolder_name)
    
    def _write_batch(
        self, 
        batch_data: List[List[Union[int, str, None]]], 
        columns: List[str], 
        destinationfilename: str, 
        filenumber: int, 
        subfolder_name: str
    ) -> None:
        try:
            df = pd.DataFrame(batch_data, columns=columns)
            batch_filename = destinationfilename.replace('.parquet', f'_part{filenumber:04d}.parquet')
            df.to_parquet(batch_filename, index=False, engine='pyarrow')
            logging.info("            Written batch %d with %s rows to %s", filenumber, len(batch_data), os.path.basename(batch_filename))
        except Exception as e:
            raise ValidationError(f"Error writing Parquet batch {filenumber}: {e}")
    
    def _write_final_batch(
        self, 
        batch_data: List[List[Union[int, str, None]]], 
        columns: List[str], 
        destinationfilename: str, 
        filenumber: int, 
        subfolder_name: str
    ) -> None:
        try:
            df = pd.DataFrame(batch_data, columns=columns)
            if filenumber == 1:
                final_filename = destinationfilename
            else:
                final_filename = destinationfilename.replace('.parquet', f'_part{filenumber:04d}.parquet')
            df.to_parquet(final_filename, index=False, engine='pyarrow')
            logging.info("            Written final batch %d with %s rows to %s", filenumber, len(batch_data), os.path.basename(final_filename))
        except Exception as e:
            raise ValidationError(f"Error writing final Parquet batch {filenumber}: {e}")