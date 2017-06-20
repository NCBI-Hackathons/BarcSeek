#!/usr/bin/env python3

"""Utilities for reading and writing FASTQ files"""

import sys
if sys.version_info.major is not 3 and sys.version_info.minor < 5:
    sys.exit("Please use Python 3.5 or higher for this module: " + __name__)


from typing import Optional, Tuple, Any

try:
    from Bio.SeqIO import QualityIO
except ImportError as error:
    sys.exit("Please install " + error.name)


class Read(object):

    def __init__(self, read_id: str, seq: str, qual: str, rev: Optional[str]=None, rev_qual: Optional[str]=None) -> None:
        self._id = read_id
        self._seq = seq
        self._qual = qual
        self._rseq = rev
        self._rqual = rev_qual
        self._validate()

    def __repr__(self) -> str:
        return self._id

    def __hash__(self) -> int:
        return hash(self.read_id)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Read):
            return hash(self) == hash(other)
        elif isinstance(other, str):
            return self._id == other or self._seq == other
        else:
            return NotImplemented

    def _validate(self) -> None:
        if len(self._seq) != len(self._qual):
            raise ValueError("'seq' and 'qual' must be the same length")
        if self._rseq :
            if not self._rqual:
                raise ValueError("A reverse quality score must be provided with a reverse read")
            elif len(self._rseq) != len(self._rqual):
                raise ValueError("'rev' and 'rev_qual' must be the same length")

    def _is_paired(self) -> bool:
        return bool(self._rseq)

    def _forward(self) -> str:
        return self._seq

    def _reverse(self) -> str:
        return self._rseq

    def _fastq(self, reverse: bool=False) -> str:
        if reverse:
            if not self.paired:
                return None
            out = (
                '>' + self.read_id,
                self._rseq,
                '+' + self.read_id,
                self._rqual
            )
        else:
            out = (
                '>' + self.read_id,
                self._seq,
                '+' + self.read_id,
                self._qual
            )
        return '\n'.join(out)

    def _rev_fastq(self) -> str:
        return self._fastq(reverse=True)

    def add_reverse(self, seq: str, qual: str) -> None:
        """Add a reverse read and quality score"""
        self._rseq = seq
        self._rqual = qual
        self._validate()

    def trim(self, start: int, end: Optional[int]=None, reverse: bool=False):
        """Trim some sequence"""
        if end and start > end:
            raise ValueError("'start' cannot be greater than 'end'")
        if reverse:
            if not self.paired:
                raise ValueError("Cannot trim a nonexistant reverse read")
            self._rseq = self._rseq[:start] + (self._rseq[end:] if end else '')
            self._rqual = self._rqual[:start] + (self._rqual[end:] if end else '')
        else:
            self._seq = self._seq[:start] + (self._seq[end:] if end else '')
            self._qual = self._qual[:start] + (self._qual[end:] if end else '')

    read_id = property(fget=__repr__, doc='The read ID')
    forward = property(fget=_forward, doc='Forward sequence')
    reverse = property(fget=_reverse, doc='Reverse sequence')
    paired = property(fget=_is_paired, doc='Is this read paired?')
    fastq = property(fget=_fastq, doc='Read in FASTQ format')
    reverse_fastq = property(fget=_rev_fastq, doc='Reverse read in FASTQ format')


def read_fastq(fastq: str, pair: Optional[str]=None) -> Tuple[Read]:
    """Read in a FASTQ file, and optionally its pair
    'fastq' the filename for the forward or only FASTQ file
    'pair' an optional filename for the reverse FASTQ file"""
    reads = dict() # type: Dict[str, Read]
    with open(fastq, 'r') as ffile: # type: _io.TextIOWrapper
        for read in QualityIO.FastqGeneralIterator(ffile): # type: Tuple[str]
            read_id, seq, qual = read # type: str, str, str
            reads[read_id] = Read(read_id=read_id, seq=seq, qual=qual)
    if pair:
        with open(pair, 'r') as rfile: # type: _io.TextIOWrapper
            for read in QualityIO.FastqGeneralIterator(rfile): # type: Tuple[str]
                read_id, seq, qual = read # type: str, str, str
                reads[read_id].add_reverse(seq=seq, qual=qual)
    return tuple(reads.values())
