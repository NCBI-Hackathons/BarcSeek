
from dask import dataframe as dd
from dask import multiprocessing
import dask
import logging
import json

logging.basicConfig(filename='parallel.log', filemode="w", level=logging.DEBUG, format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
dask.set_options(get=multiprocessing.get)


def mangle_partition(par):
    logging.debug("in mangle_partitions")
    for row in par.head(10):
        logging.debug("row: %s", row)


def main():
    output = []
    input = "data/bigtest.fastq"
    output = "parallel.out"

    logging.debug('dataframe loading %s', input)

    df = dd.read_csv(input, blocksize=250000)
    print(df.head())
    #df.map_partitions(mangle_partition)
    #df.compute(num_processors=4)

if __name__ == "__main__":
    # execute only if run as a script
    main()