#!/usr/bin/env python3

"""Barcode Partitioner for FASTQ Files"""

# optional arguments:
#   -h, --help            show this help message and exit
#   -f FORWARD FASTQ, --forward-fastq FORWARD FASTQ
#                         Provide the forward or single-end FASTQ file (filepath)
#   -r REVERSE FASTQ, --reverse-fastq REVERSE FASTQ
#                         Provide the reverse FASTQ file [optional]
#   -s SAMPLE SHEET, --sample-sheet SAMPLE SHEET
#                         Sample table
#							output will specify output file in sample sheet
#   -b BARCODES, --barcodes BARCODES
#                         Barcodes CSV file
#   -e ERROR, --error ERROR
#                         Barcodes error rate, defaults to '2'
#
#   as this grows we can group into lists

import sys
import argparse 

if sys.version_info.major is not 3 and sys.version_info.minor < 5:
    sys.exit("Please use Python 3.5 or higher")
    
#   A function to create an argument parser
def _set_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser( # type: argparse.ArgumentParser
        description='Pull DNA barcodes from FASTQ files.'
        add_help=True
    )
    
    parser.add_argument(
        '-f',
        '--forward-fastq',
        dest='forward',
        type=str,
        default=None,
        metavar='FORWARD FASTQ',
        help="Provide a filepath for the Forward FASTQ file."
        required=True
    )

    parser.add_argument(
        '-r',
        '--reverse-fastq',
        dest='reverse',
        type=str,
        default=None,
        metavar='REVERSE FASTQ',
        help="Provide a filepath for the Reverse FASTQ file."
    )
    
    parser.add_argument(
        '-s',
        '--sample-sheet',
        dest='sample',
        type=str,
        default=None,
        metavar='SAMPLE SHEET',
        help="Provide a filepath for the Sample Sheet file."
        required=True
    )
    
    parser.add_argument(
        '-b',
        '--barcodes',
        dest='barcodes',
        type=str,
        default=None,
        metavar='BARCODES',
        help="Provide a filepath for the Barcodes CSV file."
        required=True
    )
    
    parser.add_argument(
        '-e',
        '--error',
        dest='error',
        type=int,
        default=2,
        metavar='ERROR',
        help="This is how many mismatches in the barcode we allowed before rejecting. Default is 2."
    )
    
    parser.add_argument("--verbose", help="increase output verbosity",
                    action="store_true")


if __name__ == '__main__':
    PARSER = _set_args() # type: argparse.ArgumentParser
    if not sys.argv[1:]:
        sys.exit(PARSER.print_help())
    ARGS = {key: value for key, value in vars(PARSER.parse_args()).items() if value is not None} # type: Dict[str, Any]
    main(ARGS)