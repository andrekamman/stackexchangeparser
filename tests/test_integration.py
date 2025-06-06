"""
Integration tests for the complete StackExchange Parser workflow.
"""

import os
import csv
import tempfile
import pytest
from unittest.mock import patch

from stackexchange_parser import process_stackexchange_data, CSVWriter, ParquetWriter
from stackexchange_parser.core import load_tables_config


class TestEndToEndWorkflow:
    """Test complete end-to-end processing workflows."""
    
    def test_complete_csv_workflow(self, stackexchange_site_structure, sample_config_file):
        """Test complete workflow with CSV output."""
        input_dir = stackexchange_site_structure['input_dir']
        output_dir = os.path.join(input_dir, "csv_output")
        
        writer = CSVWriter()
        
        # Process the data
        result = process_stackexchange_data(
            inputdir=input_dir,
            outputdir=output_dir,
            writer=writer,
            include_meta=False,
            config_path=sample_config_file
        )
        
        # Should create one new directory (stackoverflow.com)
        assert result == 1
        
        # Verify output directory structure
        site_output_dir = os.path.join(output_dir, "stackoverflow.com")
        assert os.path.exists(site_output_dir)
        
        # Verify CSV files were created
        posts_csv = os.path.join(site_output_dir, "Posts.csv")
        users_csv = os.path.join(site_output_dir, "Users.csv")
        comments_csv = os.path.join(site_output_dir, "Comments.csv")
        
        assert os.path.exists(posts_csv)
        assert os.path.exists(users_csv)
        assert os.path.exists(comments_csv)
        
        # Verify Posts CSV content
        with open(posts_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            posts = list(reader)
        
        assert len(posts) == 3
        assert posts[0]['Id'] == '1'
        assert posts[0]['Title'] == 'How to use Git?'
        assert posts[1]['Id'] == '2'
        assert posts[2]['Id'] == '3'
        
        # Verify Users CSV content
        with open(users_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            users = list(reader)
        
        assert len(users) == 2
        assert users[0]['DisplayName'] == 'JohnDoe'
        assert users[1]['DisplayName'] == 'JaneSmith'
        
        # Verify Comments CSV content
        with open(comments_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            comments = list(reader)
        
        assert len(comments) == 2
        assert comments[0]['Text'] == 'Great question!'
    
    def test_complete_workflow_with_meta(self, stackexchange_site_structure, sample_config_file):
        """Test complete workflow including meta sites."""
        input_dir = stackexchange_site_structure['input_dir']
        output_dir = os.path.join(input_dir, "meta_output")
        
        writer = CSVWriter()
        
        # Process with meta sites included
        result = process_stackexchange_data(
            inputdir=input_dir,
            outputdir=output_dir,
            writer=writer,
            include_meta=True,
            config_path=sample_config_file
        )
        
        # Should create two directories (main site + meta site)
        assert result == 2
        
        # Verify both directories were created
        main_site_dir = os.path.join(output_dir, "stackoverflow.com")
        meta_site_dir = os.path.join(output_dir, "meta.stackoverflow.com")
        
        assert os.path.exists(main_site_dir)
        assert os.path.exists(meta_site_dir)
        
        # Verify meta site has Posts.csv
        meta_posts = os.path.join(meta_site_dir, "Posts.csv")
        assert os.path.exists(meta_posts)
        
        with open(meta_posts, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            posts = list(reader)
        
        assert len(posts) == 1
        assert posts[0]['Title'] == 'Meta question'
    
    @pytest.mark.skipif(
        True,  # Skip by default since it requires pandas/pyarrow
        reason="Requires pandas and pyarrow dependencies"
    )
    def test_complete_parquet_workflow(self, stackexchange_site_structure, sample_config_file):
        """Test complete workflow with Parquet output."""
        input_dir = stackexchange_site_structure['input_dir']
        output_dir = os.path.join(input_dir, "parquet_output")
        
        writer = ParquetWriter(batch_size=100)  # Small batch for testing
        
        result = process_stackexchange_data(
            inputdir=input_dir,
            outputdir=output_dir,
            writer=writer,
            include_meta=False,
            config_path=sample_config_file
        )
        
        assert result == 1
        
        # Verify Parquet files were created
        site_output_dir = os.path.join(output_dir, "stackoverflow.com")
        assert os.path.exists(site_output_dir)
        
        # Should have Parquet files (may be split into parts)
        parquet_files = [f for f in os.listdir(site_output_dir) if f.endswith('.parquet')]
        assert len(parquet_files) > 0
    
    def test_workflow_with_custom_config(self, stackexchange_site_structure, temp_dir):
        """Test workflow with custom configuration limiting columns."""
        # Create custom config with fewer columns
        custom_config = {
            'tables': {
                'Posts': ['Id', 'Title', 'Score'],
                'Users': ['Id', 'DisplayName']
            }
        }
        
        import yaml
        custom_config_file = os.path.join(temp_dir, "custom.yaml")
        with open(custom_config_file, 'w') as f:
            yaml.dump(custom_config, f)
        
        input_dir = stackexchange_site_structure['input_dir']
        output_dir = os.path.join(input_dir, "custom_output")
        
        writer = CSVWriter()
        
        result = process_stackexchange_data(
            inputdir=input_dir,
            outputdir=output_dir,
            writer=writer,
            include_meta=False,
            config_path=custom_config_file
        )
        
        assert result == 1
        
        # Verify limited columns in output
        posts_csv = os.path.join(output_dir, "stackoverflow.com", "Posts.csv")
        assert os.path.exists(posts_csv)
        
        with open(posts_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames
            posts = list(reader)
        
        # Should only have the 3 configured columns
        assert set(header) == {'Id', 'Title', 'Score'}
        assert len(posts) == 3
        assert 'Body' not in header  # This column was excluded
    
    def test_workflow_error_handling(self, temp_dir):
        """Test workflow error handling with invalid input."""
        writer = CSVWriter()
        
        # Test with non-existent input directory
        with pytest.raises(FileNotFoundError):
            process_stackexchange_data(
                inputdir=os.path.join(temp_dir, "nonexistent"),
                outputdir=os.path.join(temp_dir, "output"),
                writer=writer
            )
    
    def test_workflow_empty_input_directory(self, temp_dir):
        """Test workflow with empty input directory."""
        input_dir = os.path.join(temp_dir, "empty_input")
        output_dir = os.path.join(temp_dir, "empty_output")
        os.makedirs(input_dir)
        
        writer = CSVWriter()
        
        result = process_stackexchange_data(
            inputdir=input_dir,
            outputdir=output_dir,
            writer=writer
        )
        
        # Should return 0 since no data was found
        assert result == 0
    
    def test_workflow_existing_output_directory(self, stackexchange_site_structure, sample_config_file):
        """Test workflow behavior when output directory already exists."""
        input_dir = stackexchange_site_structure['input_dir']
        output_dir = os.path.join(input_dir, "existing_output")
        
        # Pre-create the output directory structure
        site_output_dir = os.path.join(output_dir, "stackoverflow.com")
        os.makedirs(site_output_dir)
        
        writer = CSVWriter()
        
        result = process_stackexchange_data(
            inputdir=input_dir,
            outputdir=output_dir,
            writer=writer,
            include_meta=False,
            config_path=sample_config_file
        )
        
        # Should return 0 because directory already existed
        assert result == 0
        
        # But files should still be processed and written
        posts_csv = os.path.join(site_output_dir, "Posts.csv")
        assert os.path.exists(posts_csv)


class TestConfigurationIntegration:
    """Test integration with different configuration scenarios."""
    
    def test_default_configuration_loading(self):
        """Test loading and using default configuration."""
        config = load_tables_config()
        
        # Should load without errors
        assert isinstance(config, dict)
        assert len(config) > 0
        
        # Should contain expected StackExchange tables
        expected_tables = ['Posts', 'Users', 'Comments', 'Votes', 'Tags']
        for table in expected_tables:
            if table in config:  # Some tables might not be in the default config
                assert isinstance(config[table], list)
                assert len(config[table]) > 0
    
    def test_configuration_validation_integration(self, temp_dir):
        """Test configuration validation during workflow."""
        # Create invalid configuration
        invalid_config = {
            'not_tables': {
                'Posts': ['Id', 'Title']
            }
        }
        
        import yaml
        invalid_config_file = os.path.join(temp_dir, "invalid.yaml")
        with open(invalid_config_file, 'w') as f:
            yaml.dump(invalid_config, f)
        
        # Should raise validation error
        from stackexchange_parser.core import ValidationError
        with pytest.raises(ValidationError):
            load_tables_config(invalid_config_file)


class TestPerformanceAndMemory:
    """Test performance characteristics and memory usage."""
    
    def test_large_xml_handling(self, temp_dir):
        """Test handling of XML files with many rows."""
        # Create a large XML file
        large_posts_xml = '''<?xml version="1.0" encoding="utf-8"?>
<posts>'''
        
        # Add many rows
        for i in range(1000):
            large_posts_xml += f'''
  <row Id="{i+1}" PostTypeId="1" CreationDate="2008-07-31T21:42:52.667" 
       Score="{i%100}" Title="Question {i+1}" Body="&lt;p&gt;Content {i+1}&lt;/p&gt;" 
       OwnerUserId="{(i%10)+1}" Tags="&lt;test&gt;" />'''
        
        large_posts_xml += '\n</posts>'
        
        # Create site structure
        site_dir = os.path.join(temp_dir, "large_site")
        os.makedirs(site_dir)
        
        with open(os.path.join(site_dir, "Posts.xml"), 'w') as f:
            f.write(large_posts_xml)
        
        # Create minimal config
        config = {'tables': {'Posts': ['Id', 'PostTypeId', 'Score', 'Title']}}
        config_file = os.path.join(temp_dir, "config.yaml")
        
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        # Process the large file
        output_dir = os.path.join(temp_dir, "large_output")
        writer = CSVWriter()
        
        result = process_stackexchange_data(
            inputdir=temp_dir,
            outputdir=output_dir,
            writer=writer,
            config_path=config_file
        )
        
        assert result == 1
        
        # Verify all rows were processed
        posts_csv = os.path.join(output_dir, "large_site", "Posts.csv")
        assert os.path.exists(posts_csv)
        
        with open(posts_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 1000
        assert rows[0]['Id'] == '1'
        assert rows[999]['Id'] == '1000'