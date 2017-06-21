import os
import re
import matplotlib.pyplot as plt
import numpy as np

#output_directory=“/Users/josephb1/Barcode_Partitioning/test.cases/“
def stats_barc(output_directory: str):
    
    os.chdir(output_directory)
    all_files=os.listdir(output_directory)
    file_names=list(filter(lambda x: re.search(r'fastq', x), all_files))
    output_dirs=[output_directory + s for s in file_names]

    output_size = []
    for i in range(len(output_dirs)):
            counts = sum(1 for line in open(output_dirs[i]))
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
    final_plot.savefig("demultiplexedResults.pdf", bbox_inches='tight')

