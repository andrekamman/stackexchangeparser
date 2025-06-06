import argparse
import sys
import logging
from .core import setup_logging, StackExchangeParserError, ConfigurationError, ValidationError
from .writers import CSVWriter, ParquetWriter
from . import process_stackexchange_data, __version__

def create_parser():
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert StackExchange XML dumps to CSV or Parquet format"
    )
    parser.add_argument(
        "inputdir", 
        help="Location of the StackExchange files or subfolders"
    )
    parser.add_argument(
        "outputdir", 
        help="Export destination folder where subfolders will be created"
    )
    parser.add_argument(
        "-f", "--format", 
        choices=["csv", "parquet"], 
        default="csv",
        help="Output format (default: csv)"
    )
    parser.add_argument(
        "-m", "--meta", 
        help="Also export the meta files", 
        action="store_true"
    )
    parser.add_argument(
        "-p", "--progressindicatorvalue", 
        help="Shows nr of rows imported for larger files", 
        type=int, 
        default=10000000
    )
    parser.add_argument(
        "-b", "--batchsize", 
        help="Number of rows per parquet file (parquet format only)", 
        type=int, 
        default=1000000
    )
    parser.add_argument(
        "-c", "--config", 
        help="Path to YAML config file with table definitions", 
        type=str, 
        default=None
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"stackexchange-parser {__version__}"
    )
    return parser

def main(args=None):
    """Main CLI function that can accept arguments or parse from command line."""
    if args is None:
        parser = create_parser()
        args = parser.parse_args()
    
    setup_logging()
    
    try:
        # Create appropriate writer based on format
        if args.format == "csv":
            writer = CSVWriter()
        elif args.format == "parquet":
            writer = ParquetWriter(
                progress_indicator_value=args.progressindicatorvalue, 
                batch_size=args.batchsize
            )
        else:
            print(f"Error: Unsupported format '{args.format}'. Use 'csv' or 'parquet'.", file=sys.stderr)
            sys.exit(1)
        
        # Process the data
        return process_stackexchange_data(
            inputdir=args.inputdir,
            outputdir=args.outputdir,
            writer=writer,
            include_meta=args.meta,
            config_path=args.config
        )
        
    except ConfigurationError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValidationError as e:
        print(f"Validation Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ImportError as e:
        print(f"Dependency Error: {e}", file=sys.stderr)
        print("Install missing dependencies with: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logging.exception("Unexpected error occurred")
        print(f"Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)

def cli_main():
    """Entry point for console script."""
    main()

if __name__ == "__main__":
    main()