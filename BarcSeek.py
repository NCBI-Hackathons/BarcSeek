#!/usr/bin/env python3

"""Parition a FASTQ file (or paired FASTQ files) based on barcodes"""

import sys
import argparse
import csv
from itertools import chain, islice
from collections import Counter
import json
import regex

from partition import IUPAC_CODES


if sys.version_info.major is not 3 and sys.version_info.minor < 5:
    sys.exit("Please use Python 3.5 or higher")

class InputError(Exception):
    '''An error occurred because of your input'''
    def __init__(self, message):
        super().__init__(self)
        self.message = message


#   A function to create an argument parser
def _set_args():
    parser = argparse.ArgumentParser( # type: argparse.ArgumentParser
        description=r'''
                     -----------------------------------
                    < Pull DNA barcodes from FASTQ files >
                     -----------------------------------
                     /
     \ ______/ V`-, /
      }        /~~
     /_)^ --,r'
    |b      |b
     ''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True
    )
    parser.add_argument(
        '-f',
        '--forward-fastq',
        dest='forward',
        type=str,
        default=None,
        metavar='FORWARD FASTQ',
        help="Provide a filepath for the Forward FASTQ file.",
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
        help="Provide a filepath for the Sample Sheet file.",
        required=True
    )
    parser.add_argument(
        '-b',
        '--barcodes',
        dest='barcodes',
        type=str,
        default=None,
        metavar='BARCODES',
        help="Provide a filepath for the Barcodes CSV file.",
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
    parser.add_argument(
        "--verbose",
        help="increase output verbosity",
        action="store_true"
    )
    return parser


def expand_iupac(barcode):
    '''
    Expand IUPAC codes, i.e. turn 'AY' to ['AC', 'AT']
    '''
    barcode = barcode.upper()
    if all((i in 'ACGTN' for i in set(barcode))):
        return barcode
    else:
        pos = regex.search(r'[%s]' % ''.join(IUPAC_CODES.keys()), barcode).start()
        code = barcode[pos]
        return (expand_iupac(barcode.replace(code, i, 1)) for i in IUPAC_CODES[code])


def unpack(collection):
    '''
    Unpack a series of nested lists, sets, or tuples
    '''
    result = [] # type: List
    for item in collection:
        if isinstance(item, (list, set, tuple)):
            result.extend(unpack(collection=item))
        else:
            result.append(item)
    return result


def barcode_check(barcode_dict):
    '''
    Checks whether or not there are barcodes in use that are ambiguous and could thus recognize the same sequence.
    For example the barcodes 'AY' and 'AW' both recognize 'AT'
    '''
    barcodes = chain.from_iterable(barcode_dict.values())
    expanded_barcodes = unpack(expand_iupac(bc) for bc in barcodes)
    multiplicate_barcodes = dict(filter(lambda item: item[1] > 1 , Counter(expanded_barcodes).items()))
    return multiplicate_barcodes


def extract_barcodes(sample_sheet, barcode_csv):
    '''
    Returns a dictionary, Keys are the sample_names,
    '''
    barcode_file = csv.reader(open(barcode_csv), delimiter=',')
    ss_file = list(csv.reader(open(sample_sheet), delimiter='\t'))[1:]
    csv_dict = {int(line[0]): line[1] for line in barcode_file}
    ss_dict = {samplename: [] for samplename in islice(chain.from_iterable(ss_file), 2, None, 3)}
    for line in ss_file:
        barcode1, barcode2, samplename = line[0], line[1], line[2]
        if barcode1:
            ss_dict[samplename].append(csv_dict[int(barcode1)])
        if barcode2:
            ss_dict[samplename].append(csv_dict[int(barcode2)])
    filtered_barcodes = list(filter(lambda sample: not(sample[1]), ss_dict.items()))
    if filtered_barcodes:
        raise InputError('One of your samples in your sample_sheet.tab has no barcodes associated with itself.')
    return ss_dict


def main(args):
    '''Run the program'''
    barcode_ambiguity_dict = barcode_check(extract_barcodes(args['sample'], args['barcodes']))
    if barcode_ambiguity_dict:
        raise InputError("There are ambiguous barcodes \n" + str(json.dumps(barcode_ambiguity_dict, indent=2)))
    #call the parallel layer which does the work:


if __name__ == '__main__':
    PARSER = _set_args() # type: argparse.ArgumentParser
    if not sys.argv[1:]:
        sys.exit(PARSER.print_help())
    ARGS = {key: value for key, value in vars(PARSER.parse_args()).items() if value is not None} # type: Dict[str, Any]
    main(ARGS)
