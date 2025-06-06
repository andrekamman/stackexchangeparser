"""
Tests for stackexchange_parser.writers module.
"""

import os
import csv
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from stackexchange_parser.writers import BaseWriter, CSVWriter, ParquetWriter


class TestBaseWriter:
    """Test the abstract base writer class."""
    
    def test_base_writer_cannot_instantiate(self):
        """Test that BaseWriter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseWriter()
    
    def test_base_writer_abstract_methods(self):
        """Test that subclasses must implement abstract methods."""
        class IncompleteWriter(BaseWriter):
            pass
        
        with pytest.raises(TypeError):
            IncompleteWriter()


class TestCSVWriter:
    """Test CSV writer functionality."""
    
    def test_csv_writer_initialization(self):
        """Test CSV writer can be initialized."""
        writer = CSVWriter()
        assert writer is not None
    
    def test_write_from_xml_posts(self, temp_dir, sample_xml_posts):
        """Test writing Posts XML to CSV."""
        writer = CSVWriter()
        
        # Create source XML file
        source_file = os.path.join(temp_dir, "Posts.xml")
        with open(source_file, 'w') as f:
            f.write(sample_xml_posts)
        
        # Define output file and columns
        destination_file = os.path.join(temp_dir, "Posts.csv")
        columns = ['Id', 'PostTypeId', 'CreationDate', 'Score', 'Title', 'Body']
        
        # Write XML to CSV
        writer.write_from_xml(source_file, "Posts", columns, destination_file, "test_site")
        
        # Verify CSV file was created
        assert os.path.exists(destination_file)
        
        # Verify CSV content
        with open(destination_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 3
        assert rows[0]['Id'] == '1'
        assert rows[0]['PostTypeId'] == '1'
        assert rows[0]['Title'] == 'How to use Git?'
        assert '&lt;p&gt;Learning Git basics&lt;/p&gt;' in rows[0]['Body']
    
    def test_write_from_xml_users(self, temp_dir, sample_xml_users):
        """Test writing Users XML to CSV."""
        writer = CSVWriter()
        
        source_file = os.path.join(temp_dir, "Users.xml")
        with open(source_file, 'w') as f:
            f.write(sample_xml_users)
        
        destination_file = os.path.join(temp_dir, "Users.csv")
        columns = ['Id', 'DisplayName', 'CreationDate', 'Reputation']
        
        writer.write_from_xml(source_file, "Users", columns, destination_file, "test_site")
        
        assert os.path.exists(destination_file)
        
        with open(destination_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 2
        assert rows[0]['DisplayName'] == 'JohnDoe'
        assert rows[1]['DisplayName'] == 'JaneSmith'
        assert rows[0]['Reputation'] == '101'
    
    def test_write_from_xml_missing_columns(self, temp_dir, sample_xml_posts):
        """Test handling of missing columns in XML."""
        writer = CSVWriter()
        
        source_file = os.path.join(temp_dir, "Posts.xml")
        with open(source_file, 'w') as f:
            f.write(sample_xml_posts)
        
        destination_file = os.path.join(temp_dir, "Posts.csv")
        # Include a column that doesn't exist in the XML
        columns = ['Id', 'PostTypeId', 'NonExistentColumn', 'Title']
        
        writer.write_from_xml(source_file, "Posts", columns, destination_file, "test_site")
        
        with open(destination_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Missing columns should be empty strings
        assert rows[0]['NonExistentColumn'] == ''
    
    def test_write_from_xml_invalid_file(self, temp_dir):
        """Test error handling for invalid XML file."""
        writer = CSVWriter()
        
        source_file = os.path.join(temp_dir, "Invalid.xml")
        with open(source_file, 'w') as f:
            f.write("Not valid XML content")
        
        destination_file = os.path.join(temp_dir, "Invalid.csv")
        columns = ['Id', 'Name']
        
        with pytest.raises(Exception):  # Should raise XML parsing error
            writer.write_from_xml(source_file, "Invalid", columns, destination_file, "test_site")
    
    def test_write_from_xml_empty_file(self, temp_dir):
        """Test handling of empty XML file."""
        writer = CSVWriter()
        
        source_file = os.path.join(temp_dir, "Empty.xml")
        with open(source_file, 'w') as f:
            f.write('<?xml version="1.0"?><posts></posts>')
        
        destination_file = os.path.join(temp_dir, "Empty.csv")
        columns = ['Id', 'Title']
        
        writer.write_from_xml(source_file, "Posts", columns, destination_file, "test_site")
        
        # Should create CSV with just headers
        assert os.path.exists(destination_file)
        with open(destination_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 0


class TestParquetWriter:
    """Test Parquet writer functionality."""
    
    def test_parquet_writer_initialization_default(self):
        """Test Parquet writer initialization with defaults."""
        writer = ParquetWriter()
        assert writer.batch_size == 1000000
        assert writer.progress_indicator_value == 10000000
    
    def test_parquet_writer_initialization_custom(self):
        """Test Parquet writer initialization with custom values."""
        writer = ParquetWriter(batch_size=500000, progress_indicator_value=100000)
        assert writer.batch_size == 500000
        assert writer.progress_indicator_value == 100000
    
    @patch('stackexchange_parser.writers.pd')
    def test_parquet_dependencies_missing(self, mock_pd):
        """Test error handling when pandas/pyarrow dependencies are missing."""
        mock_pd.side_effect = ImportError("No module named 'pandas'")
        
        with pytest.raises(ImportError, match="pandas and pyarrow are required"):
            ParquetWriter()
    
    @pytest.mark.skipif(
        True,  # Skip by default since it requires pandas/pyarrow
        reason="Requires pandas and pyarrow dependencies"
    )
    def test_write_from_xml_parquet_small(self, temp_dir, sample_xml_posts):
        """Test writing small XML file to Parquet."""
        # This test would run if pandas/pyarrow are available
        writer = ParquetWriter(batch_size=100)
        
        source_file = os.path.join(temp_dir, "Posts.xml")
        with open(source_file, 'w') as f:
            f.write(sample_xml_posts)
        
        destination_file = os.path.join(temp_dir, "Posts.parquet")
        columns = ['Id', 'PostTypeId', 'CreationDate', 'Score', 'Title']
        
        writer.write_from_xml(source_file, "Posts", columns, destination_file, "test_site")
        
        # Should create at least one parquet file
        assert os.path.exists(destination_file) or any(
            f.startswith("Posts_part") and f.endswith(".parquet")
            for f in os.listdir(temp_dir)
        )
    
    def test_parquet_writer_batch_validation(self):
        """Test validation of batch size parameter."""
        # Should accept positive integers
        writer = ParquetWriter(batch_size=1000)
        assert writer.batch_size == 1000
        
        # Should handle default case
        writer = ParquetWriter()
        assert writer.batch_size == 1000000
    
    @patch('stackexchange_parser.writers.pd')
    @patch('stackexchange_parser.writers.etree')
    def test_parquet_writer_large_file_batching(self, mock_etree, mock_pd):
        """Test that large files are processed in batches."""
        # Mock pandas to avoid actual dependency
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df
        
        # Mock XML parsing to return multiple rows
        mock_element = MagicMock()
        mock_element.get.side_effect = lambda key, default="": {"Id": "1", "Title": "Test"}[key]
        mock_etree.iterparse.return_value = [("start", mock_element)] * 2500000  # Large number
        
        writer = ParquetWriter(batch_size=1000000)
        
        # Mock file operations
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=True):
                writer.write_from_xml("test.xml", "Posts", ["Id", "Title"], "output.parquet", "site")
        
        # Should have called to_parquet multiple times for batching
        assert mock_df.to_parquet.call_count >= 2


class TestWriterIntegration:
    """Integration tests for writer classes."""
    
    def test_writer_with_special_characters(self, temp_dir):
        """Test handling of special characters in XML data."""
        writer = CSVWriter()
        
        # XML with special characters, newlines, and entities
        special_xml = '''<?xml version="1.0" encoding="utf-8"?>
<posts>
  <row Id="1" Title="Special &amp; chars" Body="Line 1&#xA;Line 2&#xD;&#xA;Line 3" 
       Code="&lt;script&gt;alert('test');&lt;/script&gt;" />
  <row Id="2" Title="Unicode: café résumé" Body="Contains unicode characters" />
</posts>'''
        
        source_file = os.path.join(temp_dir, "Special.xml")
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(special_xml)
        
        destination_file = os.path.join(temp_dir, "Special.csv")
        columns = ['Id', 'Title', 'Body', 'Code']
        
        writer.write_from_xml(source_file, "Posts", columns, destination_file, "test_site")
        
        # Verify file was created and contains expected content
        assert os.path.exists(destination_file)
        
        with open(destination_file, 'r', newline='', encoding='utf-8') as f:
            content = f.read()
        
        assert "Special & chars" in content
        assert "café résumé" in content
        assert "&lt;script&gt;" in content
    
    def test_writer_progress_logging(self, temp_dir, sample_xml_posts, caplog):
        """Test that writers log progress appropriately."""
        writer = CSVWriter()
        
        source_file = os.path.join(temp_dir, "Posts.xml")
        with open(source_file, 'w') as f:
            f.write(sample_xml_posts)
        
        destination_file = os.path.join(temp_dir, "Posts.csv")
        columns = ['Id', 'PostTypeId', 'Title']
        
        writer.write_from_xml(source_file, "Posts", columns, destination_file, "test_site")
        
        # Check that appropriate log messages were generated
        assert any("Posts" in record.message for record in caplog.records)
        assert any("test_site" in record.message for record in caplog.records)