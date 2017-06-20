#!/usr/bin/env python3

"""Paritioning functions"""

import sys
if sys.version_info.major is not 3 and sys.version_info.minor < 5:
    sys.exit("Please use Python 3.5 or higher for this program")


import itertools
from typing import Optional

try:
    import regex
except ImportError as error:
    sys.exit("Please install " + error.name)


def fix_iupac(barcode: str) -> str:
    """Remove IUPAC codes from the barcode sequence, 'N's will remain"""
    iupac = {
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
    new_barcode = barcode
    for code, sub in iupac.items(): # type: str, str
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
            min_err = max(len(subpattern) - error_rate, 0) # type: int
            barcode_pattern += '{' + str(min_err) + '<=e<=' + str(len(subpattern) + error_rate) + '}'
        pattern += barcode_pattern
        try:
            umi_pattern = '(' + ''.join(itertools.repeat('[ACGT]', umi_lengths[index])) + ')' # type: str
        except IndexError:
            break
        if error_rate:
            min_err = max(umi_lengths[index] - error_rate, 0) # type: int
            umi_pattern += '{' + str(min_err) + '<=e<=' + str(umi_lengths[index] + error_rate) + '}'
        pattern += umi_pattern
    find_barcode = regex.compile(r'%s' % pattern)
    return find_barcode
