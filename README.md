# BarcSeek ![alt text](https://i.imgur.com/Bxh9lGc.png)

A NCBI Hackathon Project Generating a Pipeline for parallel Barcode Partitioning for general use, called BarcSeek. Initial development took place at New York Genome Center, June 19-21, 2017 from a 5 person team from New York and Boston.

## Introduction
Wherever there is massive multiplexing in genomic sequencing data, a massive amount of barcode data is generated as well. Our goal through this project was to take this multiplexed genomic data and to label each transcript uniquely by partitioning the barcode data and assignng to the proper read. We aimed to sort the transcripts into individual samples using a python-based, parallel architecture pipeline.

We also aimed to make this project interface with many different barcoding strategies. We understand and have worked with many different barcode formats and we have aimed to allow our program to handle the various barcoding strategies (e.g. barcode-UMI-barcode, barcode-UMI, and handle forward & reverse reads, among others).

Once we have taken in the data (and performed the proper validation), the program takes a parallel-data-processing approach  where the input genomic data is divided up among many different workers (partitioners), taking advantage of the DASK parallel computing library for data analytics to divide the data up among the workers (which we conceptualized as the manager). The partitioners are able to use a regex to handle standard IUPAC nucleotide notations.  The workers then return a number of parsed files back to the central processing script (the manager) to be assembled and returned to the user.

## Command Line Interface Usage
```
usage: Barcodes.py [-h] -f FORWARD FASTQ [-r REVERSE FASTQ] -s SAMPLE SHEET -b
                   BARCODES [-e ERROR RATE]
                     -----------------------------------
                    < Pull DNA barcodes from FASTQ files >
                     -----------------------------------
                        _______ 
                       /       \
     \ ______/ V`-, < |  Barc!  |
      }        /~~.    \_______/
     /_)^ --,r'
    |b      |b
    
optional arguments:
  -h, --help            show this help message and exit
  -f FORWARD FASTQ, --forward-fastq FORWARD FASTQ
                        Provide the forward or single-end FASTQ file [required]
  -r REVERSE FASTQ, --reverse-fastq REVERSE FASTQ
                        Provide the reverse FASTQ file [optional]
  -s SAMPLE SHEET, --sample-sheet SAMPLE SHEET
                        Sample table, [required]
  -b BARCODES, --barcodes BARCODES
                        Barcodes CSV file, [required]
  -e ERROR RATE, --error-rate ERROR RATE
                        Barcodes error rate, [required, defaults to '2']
```

## Project Architecture
Pipeline Overview:
![alt text](https://i.imgur.com/EPEYBDq.png)

Test Case Approach: We simulated genomic data and stored it in hypothetical FASTQ files, one simulating a forward read (basic1.R1.fastq) and one simulating a reverse read (basic2.R1.fastq). Nucleotide lengths of the sample reads were:
- Sample barcodes: 6 nucleotides
- Degenerate sequences: 8 nucleotides
- Sequence of interest was 50 nucleotides. 

In essence the sequence information is the same, but the barcode and UMI information has been transposed. The schematic below provides additional information on how the test sequences were designed.
![alt text](https://i.imgur.com/jz77TaE.png)
In the sample genomic data generation, the quality scores were sampled from phred33 scale, so its likely that some barcodes nucleotides may be low enough to count as an error or, at least, uncertain. We automated generation of these test fastqs. The code for generation of these test fastq files is linked [here](/test.cases/test.case.generator.R)

The contents of these files can be found [here](/test.cases).

Command Line Interface: The command line interface takes inputs from the user to pass through the program. The inputs required are filepath for the forward read FASTQ file (-f FORWARD FASTQ, required), a filepath to the reverse FASTQ if necessary (-r REVERSE FASTQ, optional), a filepath to the sample_sheet.tab file (-s SAMPLE SHEET, required), a barcode.csv file (-b BARCODES, required), and an error rate (-e ERROR RATE, required but defaults to 2).

The command line interface provides some sanity checks, including checking to ensure there are no ambiguous barcodes that could be misinterpreted and possibly assigned to the wrong sample read. The command line interface also uses regex to have the ability to check the barcode sequences to handle IUPAC degenerate nucleotide codes (e.g. [link] (http://www.bioinformatics.org/sms/iupac.html))

Parallelization:

Partitioning:

Output:

## Sample Input Files
- Sample FASTQ File: [link](/test.cases/FASTQ_short_example.txt)
- Sample Barcode.csv: [link](barcodes_csv.txt)
- Sample sample_sheet.tab: [link](Sample_sheet.txt)

## Software Dependencies
- Python 3.5 [link](https://www.python.org/downloads/release/python-350/)
- DASK: [link](http://dask.pydata.org/en/latest/)
- Regex: [link](https://pypi.python.org/pypi/regex/)

## Resources
- Introduction to Sequencing: [link](https://www.illumina.com/content/dam/illumina-marketing/documents/products/illumina_sequencing_introduction.pdf)
- Markdown Language / Cheat Sheet: [link](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
- 

## Future Directions
- Statistics and Quality Control. Investigate and report reads per sample and average data quality.
- Uniform exception handling
- Managing whitespace considerations in CLI file & making code compatible with Python style guide. [(link)](http://legacy.python.org/dev/peps/pep-0008/)
- Add wiki-style section to provide use cases using various FASTQ files & barcoding strategies. [(link)](https://github.com/mojaveazure/angsd-wrapper/wiki)

# ![alt text](https://i.imgur.com/wBCpsf8.png) 
