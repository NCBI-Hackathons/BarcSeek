#!/usr/bin/env python3

import string
import glob
import dask
import sys
from dask import multiprocessing, delayed
import logging
import json

logging.basicConfig(filename='parallel.log', filemode="w", level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
dask.set_options(get=dask.multiprocessing.get)


@dask.delayed
def partition(filename:string):
    logging.debug("loading file: %s", filename)
    i = 0
    with open(filename, 'r') as f:
        for line in f:
            i = i + 1
    f.close()
    logging.debug("number of lines in file: %i", i)



@dask.delayed
def store(results, fn):
    logging.debug("writing results to file: %s", fn)
    #with open(fn, 'a') as f:
    #    json.dump(results, f)


def main():
    try:
        results = []
        filenames = [i for i in glob.glob("data/*.fastq")]
        assert len(filenames) > 0
        for f in filenames:
            d = delayed(partition)(f)
            logging.debug(d)
            results.append(d)
        runme = delayed(store)(results, "data/results.out")
        logging.debug(runme)
        runme.compute(num_workers=4)
    except:
        logging.error(sys.exc_info())


if __name__ == "__main__":
    # execute only if run as a script
    main()