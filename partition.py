#!/usr/bin/env python3

"""Paritioning functions"""

import sys
if sys.version_info.major is not 3 and sys.version_info.minor < 5:
    sys.exit("Please use Python 3.5 or higher for this program")


import os
import itertools
from copy import deepcopy
from typing import Optional, Union, Tuple, List, Dict

import fastq

try:
    import regex
except ImportError as error:
    sys.exit("Please install " + error.name)


IUPAC_CODES = { # type: Dict[str, str]
    'R': 'AG',
    'Y': 'CT',
    'S': 'GC',
    'W': 'AT',
    'K': 'GT',
    'M': 'AC',
    'B': 'CGT',
    'D': 'AGT',
    'H': 'ACT',
    'V': 'ACG'
}

def fix_iupac(barcode: str) -> str:
    """Remove IUPAC codes from the barcode sequence, 'N's will remain
    barcode [str]   The barcode sequence to remove IUPAC codes from
                        These codes will be replaced with regex-style options
    """
    new_barcode = barcode # type: str
    for code, sub in IUPAC_CODES.items(): # type: str, str
        new_barcode = new_barcode.replace(code, '[%s]' % sub) # type: str
    return new_barcode


def barcode_to_regex(barcode: str, error_rate: Optional[int]=None):
    """Convert a barcode string to a regex pattern
    barcode [str]           The barcode string to turn into a regex
    error_rate [int]=None   The error rate"""
    pattern = '' # type: str
    umi = regex.findall(r'(N+)', barcode, regex.IGNORECASE) # type: List[str]
    umi_lengths = tuple(map(len, umi)) # type: Tuple[int]
    filtered_barcode = filter(None, barcode.upper().split('N')) # type: filter
    for index, subpattern in enumerate(filtered_barcode): # type: int, str
        barcode_pattern = '(' + subpattern + ')' # type: str
        if error_rate:
            barcode_pattern += '{e<=' + str(error_rate) + '}'
        pattern += barcode_pattern
        try:
            umi_pattern = '(' + ''.join(itertools.repeat('[ACGT]', umi_lengths[index])) + ')' # type: str
        except IndexError:
            break
        else:
            if error_rate:
                umi_pattern += '{e<=' + str(error_rate) + '}'
            pattern += umi_pattern
    find_barcode = regex.compile(r'%s' % pattern, regex.ENHANCEMATCH)
    return find_barcode


def match_barcode(read: fastq.Read, barcodes: Union[Tuple[str], List[str]], error_rate: Optional[int]=None) -> Optional[fastq.Read]:
    """Match a read to a specific pair of barcodes
    read [fastq.Read]                           A read object to try matching with this set of barcodes
    barcodes [Collection[str, Optional[str]]]:  A tuple or list of one or two barcode sequences
    error_rate [int]=None                       The error rate
    """
    barcodes = filter(None, barcodes) # type: filter
    regexes = tuple(map(lambda tup: barcode_to_regex(*tup), zip(barcodes, itertools.repeat(error_rate)))) # type: Tuple
    matches = list() # type: List
    if len(regexes) == 1:
        matches.append(regexes[0].search(read.forward))
    elif len(regexes) == 2:
        matches.append(regexes[0].search(read.forward))
        matches.append(regexes[1].search(read.reverse))
    else:
        raise ValueError("There only be one or two barcodes")
    try:
        trimmed = deepcopy(read) # type: fastq.Read
        for index, reg in enumerate(regexes): # type: int, _regex.Pattern
            reverse = bool(index % 2) # type: bool
            for i in range(reg.groups): # type: int
                if i % 2 != 0:
                    continue
                start, end = matches[index].span(i + 1) # type: int, int
                trimmed.trim(start=start, end=end, reverse=reverse)
    except AttributeError:
        return None
    return trimmed


def partition(
        barcodes: Dict[str, List[str]],
        filename: str,
        reverse: Optional[str]=None,
        error_rate: Optional[int]=None
) -> List[Tuple[str, Optional[str]]]:
    """Partition a FASTQ file into component barcodes
    barcodes [Dict[str, List[str]]]:    A dictionary where the key is the sample ID and
                                            the value is a list or tuple of one or two
                                            barcode sequences
    filename [str]                      Forward or single FASTQ filename
    reverse [str]=None                  Optional reverse FASTQ filename
    error_rate [int]=None               The error rate
    """
    try:
        reads = fastq.read_fastq(fastq=filename, pair=reverse) # type: Tuple[fastq.Read]
    except FileNotFoundError as error:
        sys.exit("Cannot find " + error.filename)
    output_directory = os.path.dirname(filename) # type: str
    output_list = list() # type: List[Tuple[str, Optional[str]]]
    for sample_name, barcode_list in barcodes.items(): # type: str, List[str]
        #   Create output names for forward and reverse files
        output_name = output_directory + '/' + sample_name + '_fwd.fastq' # type: str
        if reverse:
            reverse_name = output_name.replace('fwd', 'rev') # type: str
            rfile = open(reverse_name, 'w') # type: _io.TextIOWrapper
        else:
            reverse_name = None
        output_list.append((output_name, reverse_name))
        #   Zip the arguments together for the map
        args = zip( # type: sip
            reads,
            itertools.repeat(barcode_list),
            itertools.repeat(error_rate)
        )
        #   Run the partitioning for each read for this barcode
        results = map(lambda tup: match_barcode(*tup), args) # type: map
        with open(output_name, 'w') as ofile: # type: _io.TextIOWrapper
            for read in filter(None, results): # type: fastq.Read
                ofile.write(read.fastq)
                ofile.write('\n')
                ofile.flush()
                if reverse:
                    rfile.write(read.reverse_fastq)
                    rfile.write('\n')
                    rfile.flush()
        if reverse:
            rfile.close()
    return output_list
