"""
Tests for stackexchange_parser.cli module.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from argparse import Namespace

from stackexchange_parser.cli import create_parser, main


class TestCreateParser:
    """Test CLI argument parser creation."""
    
    def test_create_parser_basic(self):
        """Test that parser is created with expected arguments."""
        parser = create_parser()
        
        # Test with minimal required arguments
        args = parser.parse_args(['input_dir', 'output_dir'])
        
        assert args.inputdir == 'input_dir'
        assert args.outputdir == 'output_dir'
        assert args.format == 'csv'  # default
        assert args.meta is False  # default
        assert args.config is None  # default
        assert args.progressindicatorvalue == 10000000  # default
        assert args.batchsize == 1000000  # default
    
    def test_create_parser_all_options(self):
        """Test parser with all options specified."""
        parser = create_parser()
        
        args = parser.parse_args([
            'input', 'output',
            '-f', 'parquet',
            '-m',
            '-c', 'custom.yaml',
            '-p', '5000000',
            '-b', '500000'
        ])
        
        assert args.inputdir == 'input'
        assert args.outputdir == 'output'
        assert args.format == 'parquet'
        assert args.meta is True
        assert args.config == 'custom.yaml'
        assert args.progressindicatorvalue == 5000000
        assert args.batchsize == 500000
    
    def test_create_parser_format_choices(self):
        """Test that format argument only accepts valid choices."""
        parser = create_parser()
        
        # Valid formats
        args = parser.parse_args(['input', 'output', '-f', 'csv'])
        assert args.format == 'csv'
        
        args = parser.parse_args(['input', 'output', '-f', 'parquet'])
        assert args.format == 'parquet'
        
        # Invalid format should raise error
        with pytest.raises(SystemExit):
            parser.parse_args(['input', 'output', '-f', 'invalid'])
    
    def test_create_parser_missing_required(self):
        """Test parser error with missing required arguments."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args([])  # Missing both required args
        
        with pytest.raises(SystemExit):
            parser.parse_args(['input_only'])  # Missing output dir
    
    def test_create_parser_help(self):
        """Test that help option works."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(['-h'])
    
    def test_create_parser_numeric_validation(self):
        """Test validation of numeric arguments."""
        parser = create_parser()
        
        # Valid numeric values
        args = parser.parse_args(['input', 'output', '-p', '1000', '-b', '2000'])
        assert args.progressindicatorvalue == 1000
        assert args.batchsize == 2000
        
        # Invalid numeric values should raise error
        with pytest.raises(SystemExit):
            parser.parse_args(['input', 'output', '-p', 'not_a_number'])
        
        with pytest.raises(SystemExit):
            parser.parse_args(['input', 'output', '-b', 'invalid'])


class TestMain:
    """Test main CLI function."""
    
    @patch('stackexchange_parser.cli.setup_logging')
    @patch('stackexchange_parser.cli.process_stackexchange_data')
    @patch('stackexchange_parser.cli.CSVWriter')
    def test_main_csv_format(self, mock_csv_writer, mock_process, mock_logging):
        """Test main function with CSV format."""
        mock_writer_instance = MagicMock()
        mock_csv_writer.return_value = mock_writer_instance
        mock_process.return_value = 3
        
        args = Namespace(
            inputdir='input',
            outputdir='output',
            format='csv',
            meta=False,
            config=None,
            progressindicatorvalue=10000000,
            batchsize=1000000
        )
        
        result = main(args)
        
        # Verify logging was setup
        mock_logging.assert_called_once()
        
        # Verify CSV writer was created
        mock_csv_writer.assert_called_once()
        
        # Verify processing was called with correct arguments
        mock_process.assert_called_once_with(
            'input', 'output', mock_writer_instance, False, None
        )
        
        assert result == 3
    
    @patch('stackexchange_parser.cli.setup_logging')
    @patch('stackexchange_parser.cli.process_stackexchange_data')
    @patch('stackexchange_parser.cli.ParquetWriter')
    def test_main_parquet_format(self, mock_parquet_writer, mock_process, mock_logging):
        """Test main function with Parquet format."""
        mock_writer_instance = MagicMock()
        mock_parquet_writer.return_value = mock_writer_instance
        mock_process.return_value = 2
        
        args = Namespace(
            inputdir='input',
            outputdir='output',
            format='parquet',
            meta=True,
            config='custom.yaml',
            progressindicatorvalue=5000000,
            batchsize=500000
        )
        
        result = main(args)
        
        # Verify logging was setup
        mock_logging.assert_called_once()
        
        # Verify Parquet writer was created with custom parameters
        mock_parquet_writer.assert_called_once_with(
            batch_size=500000,
            progress_indicator_value=5000000
        )
        
        # Verify processing was called with correct arguments
        mock_process.assert_called_once_with(
            'input', 'output', mock_writer_instance, True, 'custom.yaml'
        )
        
        assert result == 2
    
    @patch('stackexchange_parser.cli.setup_logging')
    @patch('stackexchange_parser.cli.process_stackexchange_data')
    def test_main_error_handling(self, mock_process, mock_logging):
        """Test main function error handling."""
        mock_process.side_effect = FileNotFoundError("Input directory not found")
        
        args = Namespace(
            inputdir='nonexistent',
            outputdir='output',
            format='csv',
            meta=False,
            config=None,
            progressindicatorvalue=10000000,
            batchsize=1000000
        )
        
        with pytest.raises(FileNotFoundError):
            main(args)
        
        # Logging should still be setup even if processing fails
        mock_logging.assert_called_once()
    
    @patch('stackexchange_parser.cli.setup_logging')
    @patch('stackexchange_parser.cli.process_stackexchange_data')
    @patch('stackexchange_parser.cli.CSVWriter')
    def test_main_with_all_options(self, mock_csv_writer, mock_process, mock_logging):
        """Test main function with all options specified."""
        mock_writer_instance = MagicMock()
        mock_csv_writer.return_value = mock_writer_instance
        mock_process.return_value = 1
        
        args = Namespace(
            inputdir='/path/to/input',
            outputdir='/path/to/output',
            format='csv',
            meta=True,
            config='/path/to/config.yaml',
            progressindicatorvalue=1000000,
            batchsize=250000
        )
        
        result = main(args)
        
        # Verify all arguments were passed correctly
        mock_process.assert_called_once_with(
            '/path/to/input',
            '/path/to/output',
            mock_writer_instance,
            True,  # include_meta
            '/path/to/config.yaml'
        )
        
        assert result == 1


class TestCLIIntegration:
    """Integration tests for CLI functionality."""
    
    @patch('stackexchange_parser.cli.setup_logging')
    @patch('stackexchange_parser.cli.process_stackexchange_data')
    @patch('stackexchange_parser.cli.CSVWriter')
    def test_cli_end_to_end_csv(self, mock_csv_writer, mock_process, mock_logging):
        """Test complete CLI workflow for CSV output."""
        mock_writer_instance = MagicMock()
        mock_csv_writer.return_value = mock_writer_instance
        mock_process.return_value = 5
        
        # Simulate command line arguments
        parser = create_parser()
        args = parser.parse_args(['test_input', 'test_output', '-f', 'csv', '-m'])
        
        result = main(args)
        
        assert result == 5
        mock_csv_writer.assert_called_once()
        mock_process.assert_called_once_with(
            'test_input', 'test_output', mock_writer_instance, True, None
        )
    
    @patch('stackexchange_parser.cli.setup_logging')
    @patch('stackexchange_parser.cli.process_stackexchange_data')
    @patch('stackexchange_parser.cli.ParquetWriter')
    def test_cli_end_to_end_parquet(self, mock_parquet_writer, mock_process, mock_logging):
        """Test complete CLI workflow for Parquet output."""
        mock_writer_instance = MagicMock()
        mock_parquet_writer.return_value = mock_writer_instance
        mock_process.return_value = 3
        
        # Simulate command line arguments with all options
        parser = create_parser()
        args = parser.parse_args([
            'input_dir', 'output_dir',
            '-f', 'parquet',
            '-c', 'config.yaml',
            '-p', '2000000',
            '-b', '100000'
        ])
        
        result = main(args)
        
        assert result == 3
        mock_parquet_writer.assert_called_once_with(
            batch_size=100000,
            progress_indicator_value=2000000
        )
        mock_process.assert_called_once_with(
            'input_dir', 'output_dir', mock_writer_instance, False, 'config.yaml'
        )
    
    def test_cli_parser_defaults(self):
        """Test that parser provides sensible defaults."""
        parser = create_parser()
        args = parser.parse_args(['input', 'output'])
        
        # Check all defaults are reasonable
        assert args.format == 'csv'
        assert args.meta is False
        assert args.config is None
        assert args.progressindicatorvalue == 10000000
        assert args.batchsize == 1000000
        
        # These should be large enough for most use cases
        assert args.progressindicatorvalue > 1000000
        assert args.batchsize > 100000