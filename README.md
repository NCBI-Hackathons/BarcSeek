# BarSeek
A NCBI Hackathon Project Generating a Pipeline for parallel Barcode Partitioning for general use, called BarSeek. Initial development took place at New York Genome Center, June 19-21, 2017 from a 5 person team from New York and Boston.

## Introduction
Wherever there is massive multiplexing in genomic sequencing data, a massive amount of barcode data is generated. Our goal through this project was take this multiplexed data and to label each transcript uniquely by partitioning the barcode data. We aimed to sort the transcripts into individual samples using a python-based, parallel architecture pipeline.

We also aimed to make this project interface with many different barcoding strategies. We understand and have worked with many different barcode formats and we have aimed to allow our program to handle the various barcoding strategies (e.g. barcode-UMI-barcode, barcode-UMI, and handle forward & reverse reads, among others).

Once we have taken in the data (and performed the proper validation), the program takes a parallel-data-processing approach  where the input genomic data is divided up among many different workers (partitioners), taking advantage of the DASK parallel computing library for data analytics to divide the data up among the workers. The partitioners are able to use a regex to handle standard IUPAC nucleotide notations.  The workers then return a number of parsed files back to the central processing script to be assembled and returned to the user.

## Command Line Interface Usage
```
usage: Barcodes.py [-h] -f FORWARD FASTQ [-r REVERSE FASTQ] -s SAMPLE SHEET -b
                   BARCODES [-e ERROR RATE]

optional arguments:
  -h, --help            show this help message and exit
  -f FORWARD FASTQ, --forward-fastq FORWARD FASTQ
                        Provide the forward or single-end FASTQ file
  -r REVERSE FASTQ, --reverse-fastq REVERSE FASTQ
                        Provide the reverse FASTQ file [optional]
  -s SAMPLE SHEET, --sample-sheet SAMPLE SHEET
                        Sample table
  -b BARCODES, --barcodes BARCODES
                        Barcodes CSV file
  -e ERROR RATE, --error-rate ERROR RATE
                        Barcodes error rate, defaults to '2'
```

## Project Architecture
![alt text](https://i.imgur.com/JZrY1Yi.png) 

## Sample Input Files
- FASTQ File: [link](/test.cases/FASTQ_short_example.txt)
- Barcode.csv: [link](barcodes_csv.txt)
- sample_sheet.tab: [link](Sample_sheet.txt)

## Software Dependencies
- DASK: [link](http://dask.pydata.org/en/latest/)

## Resources
- Introduction to Sequencing: [link](https://www.illumina.com/content/dam/illumina-marketing/documents/products/illumina_sequencing_introduction.pdf)
- Markdown Language / Cheat Sheet: [link](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)

## Future Directions
- Statistics and Quality Control. Investigate and report reads per sample and average data quality.
- Uniform exception handling
- Managing whitespace considerations in CLI file
