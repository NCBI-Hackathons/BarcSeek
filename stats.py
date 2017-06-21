#!/usr/bin/env python3

"""Some stats for BarcSeek"""

import sys
if sys.version_info.major is not 3 and sys.version_info.minor < 5:
    sys.exit("Please use Python 3.5 or higher for this module: " + __name__)


import os
from typing import Optional, List

try:
    import numpy as np
    import matplotlib.pyplot as plt
except ImportError as error:
    sys.exit("Please install " + error.name)


def stats_barc(output_files: List[str], output_directory: Optional[str]=None) -> None:
    """
    This function generates basic stats on demultiplexed datasets.
    Currently, it takes all output files as argument in the form of a list, 
    counts the number of fastq lines per file and
    outputs a pdf file with a barplot of reads/demultiplexed dataset. The output directory 
    for this pdf file is an optional argument with default set to the directory containing 
    the fastq files.
    """
    if not output_directory:
        output_directory = os.path.dirname(output_files[0]) # type: str
    file_names = tuple(os.path.basename(file) for file in output_files) # type: List[str]
    output_size = [] # type: List[int]
    for i in range(len(output_files)):
        counts = sum(1 for line in open(output_files[i])) # type: int
        output_size.append(counts)
    divisor = 4 # type: int
    outputs = (s / divisor for s in output_size) # type: generator
    num_files = len(file_names) # type: int
    ind = np.arange(num_files)
    final_plot = plt.figure()
    plt.bar(ind, outputs, align='center', alpha=0.5)
    plt.xticks(ind, file_names, rotation=45)
    plt.ylabel('number of reads')
    plt.title('dataset names')
    plt.show()
    if output_directory[-1] != '/':
        output_directory += '/'
    final_plot.savefig(output_directory + "demultiplexedResults.pdf", bbox_inches='tight')
