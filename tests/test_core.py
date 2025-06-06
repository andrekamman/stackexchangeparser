"""
Tests for stackexchange_parser.core module.
"""

import os
import tempfile
import pytest
import yaml
from unittest.mock import patch, mock_open

from stackexchange_parser.core import (
    load_tables_config,
    setup_logging,
    find_subfolders_with_data,
    ensure_output_directory,
    get_table_files_in_folder,
    clean_text,
    StackExchangeParserError,
    ConfigurationError,
    ValidationError
)


class TestLoadTablesConfig:
    """Test table configuration loading and validation."""
    
    def test_load_default_config(self):
        """Test loading the default configuration file."""
        config = load_tables_config()
        
        assert isinstance(config, dict)
        assert 'Posts' in config
        assert 'Users' in config
        assert isinstance(config['Posts'], list)
        assert len(config['Posts']) > 0
    
    def test_load_custom_config(self, sample_config_file, sample_config):
        """Test loading a custom configuration file."""
        config = load_tables_config(sample_config_file)
        
        assert config == sample_config['tables']
        assert 'Posts' in config
        assert config['Posts'] == ['Id', 'PostTypeId', 'CreationDate', 'Score', 'Title', 'Body']
    
    def test_load_nonexistent_config(self):
        """Test error handling for missing config file."""
        with pytest.raises(ConfigurationError):
            load_tables_config("nonexistent.yaml")
    
    def test_load_invalid_yaml(self, temp_dir):
        """Test error handling for invalid YAML syntax."""
        invalid_config = os.path.join(temp_dir, "invalid.yaml")
        with open(invalid_config, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        with pytest.raises(ConfigurationError):
            load_tables_config(invalid_config)
    
    def test_load_config_missing_tables_key(self, temp_dir):
        """Test validation of config structure."""
        invalid_config = os.path.join(temp_dir, "missing_tables.yaml")
        with open(invalid_config, 'w') as f:
            yaml.dump({'not_tables': {}}, f)
        
        with pytest.raises(ValidationError):
            load_tables_config(invalid_config)
    
    def test_load_config_invalid_table_structure(self, temp_dir):
        """Test validation of table structure."""
        invalid_config = os.path.join(temp_dir, "invalid_structure.yaml")
        with open(invalid_config, 'w') as f:
            yaml.dump({'tables': {'Posts': 'not_a_list'}}, f)
        
        with pytest.raises(ValidationError):
            load_tables_config(invalid_config)


class TestSetupLogging:
    """Test logging configuration."""
    
    def test_setup_logging_default(self):
        """Test that logging setup doesn't raise errors."""
        # Should not raise any exceptions
        setup_logging()
    
    @patch('logging.basicConfig')
    def test_setup_logging_called_correctly(self, mock_basic_config):
        """Test that logging is configured with correct parameters."""
        setup_logging()
        
        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args[1]
        assert call_args['level'] == 20  # logging.INFO
        assert 'format' in call_args
        assert '%' in call_args['format']  # Should contain timestamp format


class TestFindSubfoldersWithData:
    """Test finding StackExchange data directories."""
    
    def test_find_subfolders_without_meta(self, stackexchange_site_structure, sample_config):
        """Test finding subfolders excluding meta sites."""
        input_dir = stackexchange_site_structure['input_dir']
        tables = sample_config['tables']
        
        subfolders = find_subfolders_with_data(input_dir, tables, include_meta=False)
        
        assert len(subfolders) == 1
        assert subfolders[0].endswith('stackoverflow.com')
    
    def test_find_subfolders_with_meta(self, stackexchange_site_structure, sample_config):
        """Test finding subfolders including meta sites."""
        input_dir = stackexchange_site_structure['input_dir']
        tables = sample_config['tables']
        
        subfolders = find_subfolders_with_data(input_dir, tables, include_meta=True)
        
        assert len(subfolders) == 2
        folder_names = [os.path.basename(f) for f in subfolders]
        assert 'stackoverflow.com' in folder_names
        assert 'meta.stackoverflow.com' in folder_names
    
    def test_find_subfolders_no_data(self, temp_dir, sample_config):
        """Test behavior when no StackExchange data is found."""
        tables = sample_config['tables']
        
        subfolders = find_subfolders_with_data(temp_dir, tables)
        
        assert subfolders == []
    
    def test_find_subfolders_nonexistent_directory(self, sample_config):
        """Test error handling for missing input directory."""
        tables = sample_config['tables']
        
        with pytest.raises(FileNotFoundError):
            find_subfolders_with_data("nonexistent", tables)


class TestEnsureOutputDirectory:
    """Test output directory creation."""
    
    def test_ensure_output_directory_new(self, temp_dir):
        """Test creating a new output directory."""
        output_dir = os.path.join(temp_dir, "output")
        subfolder_name = "test_site"
        
        result = ensure_output_directory(output_dir, subfolder_name)
        
        assert result is True
        assert os.path.exists(os.path.join(output_dir, subfolder_name))
    
    def test_ensure_output_directory_existing(self, temp_dir):
        """Test handling existing output directory."""
        output_dir = os.path.join(temp_dir, "output")
        subfolder_name = "test_site"
        
        # Create directory first
        os.makedirs(os.path.join(output_dir, subfolder_name))
        
        result = ensure_output_directory(output_dir, subfolder_name)
        
        assert result is False  # Directory already existed
        assert os.path.exists(os.path.join(output_dir, subfolder_name))
    
    @patch('os.makedirs')
    def test_ensure_output_directory_permission_error(self, mock_makedirs, temp_dir):
        """Test handling permission errors."""
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        output_dir = os.path.join(temp_dir, "output")
        subfolder_name = "test_site"
        
        with pytest.raises(PermissionError):
            ensure_output_directory(output_dir, subfolder_name)


class TestGetTableFilesInFolder:
    """Test finding table files in a folder."""
    
    def test_get_table_files_all_present(self, stackexchange_site_structure, sample_config):
        """Test finding all expected table files."""
        site_dir = stackexchange_site_structure['main_site']
        tables = sample_config['tables']
        
        table_files = get_table_files_in_folder(site_dir, tables)
        
        assert len(table_files) == 3  # Posts, Users, Comments
        
        # Check that all expected files are found
        table_names = [table_name for _, table_name, _ in table_files]
        assert 'Posts' in table_names
        assert 'Users' in table_names
        assert 'Comments' in table_names
        
        # Check file paths and columns
        for source_file, table_name, columns in table_files:
            assert os.path.exists(source_file)
            assert source_file.endswith(f"{table_name}.xml")
            assert columns == tables[table_name]
    
    def test_get_table_files_partial(self, temp_dir, sample_config):
        """Test finding subset of table files."""
        site_dir = os.path.join(temp_dir, "partial_site")
        os.makedirs(site_dir)
        
        # Create only Posts.xml
        with open(os.path.join(site_dir, "Posts.xml"), 'w') as f:
            f.write('<?xml version="1.0"?><posts></posts>')
        
        tables = sample_config['tables']
        table_files = get_table_files_in_folder(site_dir, tables)
        
        assert len(table_files) == 1
        assert table_files[0][1] == 'Posts'
    
    def test_get_table_files_none_present(self, temp_dir, sample_config):
        """Test behavior when no table files are found."""
        site_dir = os.path.join(temp_dir, "empty_site")
        os.makedirs(site_dir)
        
        tables = sample_config['tables']
        table_files = get_table_files_in_folder(site_dir, tables)
        
        assert table_files == []


class TestCleanText:
    """Test text cleaning functionality."""
    
    def test_clean_text_newlines(self):
        """Test newline conversion to XML entities."""
        text = "Line 1\nLine 2\rLine 3\r\nLine 4"
        result = clean_text(text)
        
        assert "\n" not in result
        assert "\r" not in result
        assert "&#xA;" in result
        assert "&#xD;" in result
    
    def test_clean_text_boolean_true(self):
        """Test True boolean conversion."""
        result = clean_text("True")
        assert result == "1"
    
    def test_clean_text_boolean_false(self):
        """Test False boolean conversion."""
        result = clean_text("False")
        assert result == "0"
    
    def test_clean_text_none(self):
        """Test None handling."""
        result = clean_text(None)
        assert result == ""
    
    def test_clean_text_normal_string(self):
        """Test normal string remains unchanged."""
        text = "Normal text without special characters"
        result = clean_text(text)
        assert result == text
    
    def test_clean_text_mixed(self):
        """Test text with multiple special cases."""
        text = "Some text\nwith True and\rFalse values"
        result = clean_text(text)
        
        assert "&#xA;" in result
        assert "&#xD;" in result
        assert "True" in result  # Should not convert True inside larger text
        assert "False" in result  # Should not convert False inside larger text