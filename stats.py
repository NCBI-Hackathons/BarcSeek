#!/usr/bin/env python3

import re
import sys
try:
    import matplotlib.pyplot as plt
except ImportError as error:
    sys.exit("Please install " + error.name)

import numpy as np
import os
from typing import Optional, List
def stats_barc(output_files: List[str], output_directory: Optional[str]=None):
    if not output_directory:
        output_directory = os.path.dirname(output_files[0])

    file_names=[os.path.basename(file) for file in output_files]

    output_size = []
    for i in range(len(output_files)):
            counts = sum(1 for line in open(output_files[i]))
            output_size.append(counts) 
    divisor = 4
    outputs = [s/divisor for s in output_size]
    N = len(file_names)
    ind = np.arange(N)
    width = 0.5
    final_plot = plt.figure()
    plt.bar(ind, outputs, align='center', alpha=0.5)
    plt.xticks(ind, file_names, rotation=45)
    plt.ylabel('number of reads')
    plt.title('dataset names')
    plt.show()

    if output_directory[-1] != '/':
        output_directory += '/'
    final_plot.savefig(output_directory + "demultiplexedResults.pdf", bbox_inches='tight')
