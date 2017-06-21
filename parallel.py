#!/usr/bin/env python3

import sys

if sys.version_info.major is not 3 and sys.version_info.minor < 5:
    sys.exit("Please use Python 3.5 or higher for this program")

import os
import glob
import dask
from dask import multiprocessing, delayed
import logging
import json
import sys
import subprocess
import shlex
import re
from time import sleep
from partition import fpartition, partition

import itertools
from typing import Optional

logging.basicConfig(filename='parallel.log', filemode="w", level=logging.DEBUG, format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger('barcode-logger')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

split_file_pattern = 'x12345_filename.fastq'

dask.set_options(get=dask.multiprocessing.get)

def _fake_partition_(filename: str):
    logger.debug("loading file: %s", filename)
    i = 0
    with open(filename, 'r') as f:
        for line in f:
            i = i + 1
    f.close()
    logger.debug("number of lines in file: %i", i)


def _read_filenames_(input_dir: str) -> dict:
    logger.debug("reading filenames from directory %s", input_dir)


def split_files(file_f: str, file_r: str):
    subprocess.run()


def _invoke_workers_(files: dict):
    logger.debug("invoking workers, number of files %i", len(files.keys()))
    # for each file, call partition()


# one output file per barcode, for forward and reverse
def _join_output_files_(output_file_dir: str):
    logger.debug("joining output files in dir %s", output_file_dir)


def _run_command_(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, bufsize=1)
    so = []
    while True:
        output = process.stdout.readline().decode()
        if output == '' and process.poll() is not None:
            break
        if output:
            so.append(output.strip())
    rc = process.poll()
    return rc, so


def _get_line_count_(fastq_fn:str) -> int:
    (rc, out) = _run_command_("wc -l %s" % fastq_fn)
    return int(out[0].split(" ")[0])


def _get_dir_fn_(fastq_file: str) -> tuple:
    if fastq_file:
        (*paths, fn) = os.path.split(fastq_file)
        return paths[0], fn
    else:
        return "", ""


''' creates files of the format x12345_filename.fastq '''
def _split_fastq_(fastq_fn: str, num_lines: int):
    (d, fn) = _get_dir_fn_(fastq_fn)
    logger.debug("chunk file num lines=%i" % num_lines)
    logger.debug("changing dir to: %s" % d)
    os.chdir(d)
    cmd = "split -d -a 5 -l %i --additional-suffix=_%s %s" % (num_lines, fn, fn)

    logger.debug("running command %s" % cmd)
    (rc, out) = _run_command_(cmd)
    return rc, out


''' creates files of the format x12345_filename.fastq '''
def _split_files_(num_lines: int, forward_fastq: str, reverse_fastq: Optional[str] = None):
    (rc, out) = _split_fastq_(forward_fastq, num_lines)
    if rc:
        raise Exception("Error splitting files, error code %s" % rc)

    if reverse_fastq:
        (rc, out) = _split_fastq_(reverse_fastq, num_lines)
        if rc:
            raise Exception("Error splitting files, error code %s" % rc)


''' files in the format x12345_filename.fastq '''
def _fetch_chunk_files_(num_lines: int, forward_fastq: str, reverse_fastq: Optional[str] = None) -> dict:
    (d, f_fn) = _get_dir_fn_(forward_fastq)

    logger.debug("fetching chunk files, changing dir to %s" % d)
    os.chdir(d)

    master_dict = {}

    _split_files_(num_lines, forward_fastq, reverse_fastq)
    logger.debug("fetching new file names")

    f_regex = 'x*_' + f_fn
    logger.debug("looking for files of pattern %s" % f_regex)
    f_files = glob.glob(f_regex)

    logger.debug("found %i files" % len(f_files))

    f_dict = {re.search('x(\d+)', fn).group(0): fn for fn in f_files}

    prefixes = list(f_dict.keys())
    prefixes.sort()
    logger.debug("num prefixes: %i" % len(prefixes))

    if (reverse_fastq):
        (d, r_fn) = _get_dir_fn_(reverse_fastq)
        r_files = glob.glob('x*_' + r_fn)
        r_files.sort()
        r_dict = {re.search('x(\d+)', fn).group(0): fn for fn in r_files}
        for p in prefixes:
            f_file = os.path.join(d, f_dict[p])
            r_file = os.path.join(d, r_dict[p])
            master_dict[p] = {'f_input': f_file, 'r_input': r_file}
    else:
        for p in prefixes:
            f_file = os.path.join(d, f_dict[p])
            master_dict[p] = {'f_input': f_file, 'r_input': None}

    return master_dict


def _sanity_checks_(num_lines:int, forward_fastq:str, reverse_fastq: Optional[str] = None):
    (fdir, ffn) = _get_dir_fn_(forward_fastq)
    (rdir, rfn) = _get_dir_fn_(reverse_fastq)
    if rdir and not (fdir == rdir):
        raise Exception("forward fastq and reverse fastq must be in same directory: %s   %s" % forward_fastq,
                        reverse_fastq)
    file_lines = _get_line_count_(forward_fastq)
    if file_lines % 4 or num_lines % 4:
        raise Exception("fastq file size, and split file size must both be a multiple of 4, you gave file: %i, split: %i"
                % (file_lines, num_lines))


def _dump_dict_(master_dict:dict):
    for p in master_dict.keys():
        f_f = master_dict[p]["f_input"]
        r_f = master_dict[p]["r_input"]
        logger.debug("prefix %s, forward: %s, reverse %s" % (p, f_f, r_f))


def _partition_(barcodes:dict, forward_fn:str, reverse_fn: Optional[str] = None):
    return partition(barcodes, forward_fn, reverse_fn)


def _reduce_(results:list):
    return results


def parallelize(barcodes:dict, num_lines:int, forward_fastq:str, reverse_fastq:Optional[str] = None):
    orig_home = os.getcwd()

    _sanity_checks_(num_lines, forward_fastq, reverse_fastq)
    master_dict  = _fetch_chunk_files_(num_lines, forward_fastq, reverse_fastq)
    _dump_dict_(master_dict)
    logger.debug("iterating over partition calls")
    results = []

    for p in sorted(master_dict):
        f_file = master_dict[p]['f_input']
        r_file = master_dict[p]['r_input']
        logger.debug("calling partition")
        result = dask.delayed(_partition_)(barcodes, f_file, r_file)
        results.append(result)

    logger.debug("calling reduce")
    the_job = dask.delayed(_reduce_)(results)
    #the_job.visualize()
    the_job.compute(num_workers=4)







'''
inputs: output file path, path to 2 fastq files, one forward, one reverse (optional)
        barcode list, sample_sheet dictionary
        TODO: number of chunks
outputs: none, or path to output files, one output file per sample

do: -- fetch list of filenames. @TODO: how to determine forward, reverse??
    -- read barcode file into an tuple of tuples
    -- read sample_sheet into dictionary?
    -- create a worker for each forward/reverse file pair
         worker:(file path1, file path2?, barcode list)
         worker produces: output files of the format barcode_inputfilename
    -- join all barcode output files into one file per barcode, for forward and reverse files
'''

def main():
    try:
        _run_command_("rm -f /home/jcabraham/python-projects/Barcode_Partitioning/data/x*")
        barcodes = {
            'sample1': ['AGTGCA' ],
            'sample2': ['TCACAG'],
            'sample1': ['AGTGCA'],
            'sample2': ['CAGATC']
        }

        num_lines = 4
        forward_fastq = "/home/jcabraham/python-projects/Barcode_Partitioning/data/tiny_f.fastq"
        #reverse_fastq = "/home/jcabraham/python-projects/Barcode_Partitioning/data/test01_r.fastq"
        parallelize(
            barcodes=barcodes,
            num_lines=num_lines,
            forward_fastq=forward_fastq
        #    reverse_fastq=reverse_fastq
        )

    except:
        print(sys.exc_info())
        logger.error(sys.exc_info())


if __name__ == "__main__":
    # execute only if run as a script
    main()
