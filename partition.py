#!/usr/bin/env python3

"""Paritioning functions"""

import sys
if sys.version_info.major is not 3 and sys.version_info.minor < 5:
    sys.exit("Please use Python 3.5 or higher for this program")


import itertools
from copy import deepcopy
from typing import Optional, Union, Tuple, List

import fastq

try:
    import regex
except ImportError as error:
    sys.exit("Please install " + error.name)


IUPAC_CODES = {
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
    """Remove IUPAC codes from the barcode sequence, 'N's will remain"""
    new_barcode = barcode
    for code, sub in IUPAC_CODES.items(): # type: str, str
        new_barcode = new_barcode.replace(code, '[%s]' % sub) # type: str
    return new_barcode


def barcode_to_regex(barcode: str, error_rate: Optional[int]=None):
    """Convert a barcode string to a regex pattern"""
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
    'read' is an object of class Read
    'barcodes' is either a tuple or list of one or two barcode sequences
    'error_rate' is the error rate"""
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
    if not matches:
        return None
    trimmed = deepcopy(read)
    for index, reg in enumerate(regexes): # type: int, _regex.Pattern
        print("trimming match #", index)
        if index % 2 != 0:
            reverse = True # type: bool
        else:
            reverse = False # type: int
        for i in range(reg.groups): # type: int
            if i % 2 != 0:
                continue
            start, end = matches[index].span(i + 1) # type: int, int
            trimmed.trim(start=start, end=end, reverse=reverse)
    return trimmed
