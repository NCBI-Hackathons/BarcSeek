
from dask import delayed


@delayed
def load(filename):
    print("loading file: %s", filename)


@delayed
def clean(data):
    pass


@delayed
def analyze(sequence_of_data):
    pass


@delayed
def store(result):
    with open('out.txt', 'w') as f:
        f.write(result)


def __main__(args):
    fastq_file = "foo.fastq".
    #files = ['myfile.a.data', 'myfile.b.data', 'myfile.c.data']
    #loaded = [load(i) for i in files]
    #cleaned = [clean(i) for i in loaded]
    #analyzed = analyze(cleaned)
    #stored = store(analyzed)

    #stored.compute()
