# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a professional-grade StackExchange data parser that converts XML dumps from StackExchange sites into CSV or Parquet format for easier data analysis and database import. The project follows Python best practices with comprehensive testing, documentation, and development tooling.

### Key Components:
- **Core module**: `stackexchange_parser/` - Python package containing shared functionality
- **Configuration**: `config/tables.yaml` - YAML file defining table schemas and column mappings
- **Main CLI**: `stackexchange_convert.py` - Unified command-line interface supporting both CSV and Parquet output
- **Legacy scripts**: `stackexchangetocsv.py` and `stackexchangetoparquet.py` - Deprecated individual format scripts (backwards compatibility)
- **SQL Server integration**: `SQLServer/` directory contains table creation scripts and bulk insert commands
- **Reference data**: `data/` directory contains CSV files for lookup tables (PostTypes, VoteTypes, etc.)
- **Testing suite**: `tests/` directory with comprehensive test coverage
- **Documentation**: `example.py` with practical usage examples
- **Development tools**: Complete setup for professional Python development

## Core Architecture

The project is built around a modular architecture with shared core functionality:

### Module Structure
- **`stackexchange_parser/core.py`**: XML parsing, file utilities, and configuration loading
- **`stackexchange_parser/writers.py`**: Writer classes for CSV and Parquet output formats
- **`stackexchange_parser/cli.py`**: Command-line interface logic separated from core functionality
- **`stackexchange_parser/__init__.py`**: Main processing workflow and public API
- **`config/tables.yaml`**: Table schema definitions and column mappings

### Processing Flow
1. **Loads table configuration** from YAML file (default or custom path)
2. **Scans input directories** recursively for StackExchange XML files
3. **Uses lxml for streaming XML parsing** to handle large files efficiently
4. **Converts XML to CSV/Parquet** with proper escaping for newlines and special characters
5. **Maps StackExchange schema** to configured table structures with specific column orders

### Key Data Structures

The table schema mapping is defined in `config/tables.yaml` and loaded dynamically by `load_tables_config()` in `stackexchange_parser/core.py:7-14`. This YAML configuration is the authoritative source for column names and order across both output formats.

### File Processing Logic

- Loads table definitions from YAML configuration file
- Recursively scans input folder for directories containing StackExchange XML files
- Processes each XML file using streaming parser to avoid memory issues
- Handles meta sites (prefixed with "meta.") separately via `-m` flag
- Creates output directory structure mirroring input structure

## Common Commands

### Main CLI Interface (Recommended)
```bash
# CSV output
python stackexchange_convert.py <input_folder> <output_folder> -f csv

# Parquet output
python stackexchange_convert.py <input_folder> <output_folder> -f parquet

# Include meta sites
python stackexchange_convert.py <input_folder> <output_folder> -f csv -m

# Custom configuration file
python stackexchange_convert.py <input_folder> <output_folder> -f parquet -c custom_tables.yaml

# Parquet with custom batch size
python stackexchange_convert.py <input_folder> <output_folder> -f parquet -b 500000

# All options combined
python stackexchange_convert.py <input_folder> <output_folder> -f parquet -c custom.yaml -b 500000 -m -p 5000000
```

### Legacy Scripts (Backwards Compatibility)
```bash
# These scripts are deprecated but still functional
python stackexchangetocsv.py <input_folder> <output_folder>
python stackexchangetoparquet.py <input_folder> <output_folder>
```

### Available CLI Options
- **`-f, --format`**: Output format (`csv` or `parquet`, default: `csv`)
- **`-m, --meta`**: Include meta sites
- **`-c, --config`**: Path to custom YAML configuration file
- **`-p, --progressindicatorvalue`**: Progress indicator interval (default: 10,000,000)
- **`-b, --batchsize`**: Rows per Parquet file (default: 1,000,000, Parquet only)
- **`--version`**: Show version information and exit

### Using as a Module (Programmatic Access)
```python
from stackexchange_parser import process_stackexchange_data, CSVWriter, ParquetWriter, load_tables_config

# Simple CSV conversion
writer = CSVWriter()
process_stackexchange_data("input/", "output/", writer)

# Advanced Parquet conversion with all options
writer = ParquetWriter(batch_size=500000, progress_indicator_value=1000000)
process_stackexchange_data(
    inputdir="input/", 
    outputdir="output/", 
    writer=writer,
    include_meta=True,
    config_path="custom_tables.yaml"
)

# Load and inspect configuration
tables = load_tables_config("config/tables.yaml")
print(f"Available tables: {list(tables.keys())}")
print(f"Posts columns: {tables['Posts']}")

# Use custom configuration
custom_tables = load_tables_config("my_custom_config.yaml")
writer = CSVWriter()
process_stackexchange_data("input/", "output/", writer, config_path="my_custom_config.yaml")
```

### Install Dependencies
```bash
# For basic CSV functionality
pip install -r requirements.txt

# For development (includes testing, formatting, linting tools)
pip install -r requirements-dev.txt

# Or install the package in development mode
pip install -e .[all]
```

### SQL Server Import
After generating CSV files, use the SQL scripts in `SQLServer/` to create tables and import data:
1. Run individual table creation scripts (e.g., `Posts.sql`)
2. Modify paths in `bulkinsert.sql` to match your output directory
3. Execute bulk insert commands

## Important Implementation Details

### Shared Core Features
- **Configurable schema**: Table definitions loaded from YAML configuration files for easy customization
- **Memory efficiency**: Uses `etree.iterparse()` with element cleanup to process large XML files without loading everything into memory
- **Character encoding**: Handles newlines and special characters by converting to XML entities (core.py:30-36)
- **Boolean conversion**: Converts XML "True"/"False" strings to 1/0 integers (core.py:30-36)
- **Progress tracking**: Configurable progress indicators for large file processing via `-p` parameter
- **Modular design**: Shared functionality in `stackexchange_parser` module eliminates code duplication
- **CLI separation**: Command-line logic separated from core functionality for easy programmatic use

### Writer Classes
- **BaseWriter**: Abstract base class defining common interface (writers.py:8-18)
- **CSVWriter**: Streaming CSV output, writes each row immediately (writers.py:20-33)
- **ParquetWriter**: Chunked Parquet output with configurable batch sizes (writers.py:35-71)

### CSV Writer Specifics
- **Streaming output**: Writes each row immediately to CSV file
- **Single file per table**: Each XML file produces one CSV file
- **Empty cell handling**: Converts None values to empty strings for CSV compatibility

### Parquet Writer Specifics
- **Chunked processing**: Processes data in configurable batches (default: 1M rows) to maintain low memory usage
- **Multiple output files**: Large tables are split into multiple Parquet files with `_part0001.parquet` naming
- **Batch size control**: Use `-b` parameter to adjust memory usage vs. file count trade-off
- **Pandas integration**: Uses pandas DataFrames for Parquet writing with PyArrow engine
- **Dependency checking**: Gracefully handles missing pandas/pyarrow dependencies

## File Dependencies

- **Core module**: Depends on `lxml>=4.9.0` for XML parsing and `pyyaml>=6.0` for configuration loading
- **CSV functionality**: No additional dependencies beyond core
- **Parquet functionality**: Requires `pandas>=1.5.0` and `pyarrow>=10.0.0` (auto-checked at runtime)
- **Production dependencies**: Specified in `requirements.txt` with version pinning
- **Development dependencies**: Comprehensive tooling in `requirements-dev.txt`
- **Configuration**: Default config at `config/tables.yaml`, customizable via `-c` parameter
- **SQL scripts**: Assume SQL Server with BULK INSERT capability (designed for CSV import)
- **Reference files**: CSV files in `data/` provide lookup values for normalized tables
- **Modern packaging**: `pyproject.toml` with full metadata and optional dependencies

## Development Notes

### Architecture Patterns
- **Separation of concerns**: CLI logic (`cli.py`) separated from core functionality for clean imports
- **Unified interface**: `stackexchange_convert.py` provides single entry point with format selection
- **Backwards compatibility**: Legacy scripts maintained but marked as deprecated
- **Pure functions**: Core processing functions accept parameters, not CLI args
- **Professional packaging**: Modern `pyproject.toml` with console script entry points
- **Type safety**: Comprehensive type hints throughout codebase
- **Error handling**: Custom exception hierarchy with detailed error messages

### Code Organization
- **Entry points**: Main CLI at `stackexchange_convert.py`, console script `stackexchange-convert`
- **Configuration flexibility**: Easy to modify table schemas or add new tables by editing YAML files
- **Extensibility**: New output formats can be added by creating new writer classes inheriting from `BaseWriter`
- **Testing**: Comprehensive test suite with unit, integration, and CLI tests
- **Documentation**: Complete examples in `example.py` and detailed docstrings
- **Path handling**: Core module uses `os.path.join()` for cross-platform compatibility
- **Code quality**: Pre-commit hooks, linting, formatting, and type checking

### Migration Guide
- **New projects**: Use `stackexchange-convert` console command or `python stackexchange_convert.py`
- **Package installation**: `pip install -e .` for development or `pip install dist/*.whl` for production
- **Existing scripts**: Continue to work but consider migrating to new interface
- **Programmatic use**: Import functions directly from `stackexchange_parser` module

## Configuration File Format

The `config/tables.yaml` file follows this structure:

```yaml
tables:
  TableName:
    - Column1
    - Column2
    - Column3
  AnotherTable:
    - Id
    - Name
    - Value
```

Custom configurations can define:
- **New tables**: Add tables not in the default StackExchange schema
- **Modified columns**: Change column order or subset of columns to extract
- **Site-specific schemas**: Different configurations for different StackExchange sites

## Development Setup and Testing

This project follows Python best practices with comprehensive tooling for development:

### Development Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd stackexchangeparser

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks (optional but recommended)
pre-commit install

# Run tests
pytest

# Run tests with coverage
pytest --cov=stackexchange_parser --cov-report=html
```

### Code Quality Tools
- **Testing**: `pytest` with comprehensive test suite in `tests/` directory
- **Code formatting**: `black` for consistent code style (industry standard)
- **Ultra-fast linting**: `ruff` - replaces flake8, isort, bandit, and more (10-100x faster)
- **Type checking**: `mypy` for static type analysis
- **Documentation**: `pydocstyle` for docstring style checks
- **Pre-commit hooks**: Automated code quality checks on commit

### Running Code Quality Checks
```bash
# Format code with Black (industry standard)
black stackexchange_parser/ tests/ example.py

# Lint and auto-fix with Ruff (ultra-fast, replaces flake8, isort, bandit)
ruff check --fix stackexchange_parser/ tests/ example.py

# Type checking
mypy stackexchange_parser/

# Documentation style
pydocstyle stackexchange_parser/

# Run all pre-commit hooks manually
pre-commit run --all-files

# One-liner for full check (recommended)
ruff check --fix . && black . && mypy stackexchange_parser/
```

### Package Installation and Distribution
```bash
# Install in development mode
pip install -e .

# Install with optional dependencies
pip install -e .[parquet]    # Parquet support
pip install -e .[dev]        # Development tools
pip install -e .[all]        # Everything

# Build package
python -m build

# Install from built package
pip install dist/stackexchange_parser-*.whl
```

### Available Console Commands
After installation, the CLI is available as a console command:
```bash
# Use the installed console command (recommended)
stackexchange-convert input/ output/ -f parquet

# Or run the module directly
python -m stackexchange_parser.cli input/ output/ -f csv

# Check version
stackexchange-convert --version
```

### Example Usage
See `example.py` for comprehensive usage examples including:
- Basic CSV and Parquet conversion
- Custom configuration files
- Error handling patterns
- Memory-efficient processing for large datasets
- Data inspection before processing
- Integration with different workflow patterns

### Testing Framework
The test suite covers:
- **Unit tests**: Individual function and class testing
- **Integration tests**: End-to-end workflow testing
- **CLI tests**: Command-line interface validation
- **Configuration tests**: YAML config loading and validation
- **Error handling**: Exception scenarios and edge cases
- **Performance tests**: Large file processing validation

Run specific test categories:
```bash
pytest tests/test_core.py        # Core functionality
pytest tests/test_writers.py     # Writer classes
pytest tests/test_cli.py         # CLI interface
pytest tests/test_integration.py # End-to-end workflows
pytest -m "not slow"             # Skip slow tests
pytest --cov-report=term-missing # Coverage with missing lines
```

## Quality Assurance

This project maintains high code quality standards:

### Current Status
- ✅ **Comprehensive test suite** - Unit, integration, and CLI tests
- ✅ **Type safety** - Complete type hints with mypy validation
- ✅ **Documentation** - Docstrings throughout and practical examples
- ✅ **Modern code quality** - Black + Ruff (ultra-fast, replaces flake8/isort/bandit)
- ✅ **Advanced linting** - 10-100x faster than traditional tools
- ✅ **Modern packaging** - pyproject.toml with proper metadata
- ✅ **Dependency management** - Version pinning and optional dependencies
- ✅ **Pre-commit hooks** - Automated quality checks
- ✅ **Professional structure** - Follows Python packaging best practices

### Continuous Integration Readiness
The project is ready for CI/CD pipelines with:
- Standardized test commands
- Code quality metrics
- Coverage reporting
- Multiple Python version support (3.8-3.12)
- Reproducible builds with pinned dependencies

### Performance Characteristics
- **Memory efficient**: Streaming XML processing for large files
- **Scalable**: Configurable batch sizes for different memory constraints
- **Progress tracking**: Built-in progress indicators for long-running operations
- **Cross-platform**: Works on Windows, macOS, and Linux