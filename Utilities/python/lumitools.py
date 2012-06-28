'''

Tools for messing about with lumis and JSON files

Author: Evan K. Friis, UW

'''

import json

def group_by_run(sorted_run_lumis):
    '''
    Generate a list of lists run-lumi tuples, grouped by run
    Example:
    >>> run_lumis = [(100, 1), (100, 2), (150, 1), (150, 2), (150, 8)]
    >>> list(group_by_run(run_lumis))
    [(100, [1, 2]), (150, [1, 2, 8])]

    '''
    current_run = None
    output = []
    for run, lumi in sorted_run_lumis:
        if current_run is None or run == current_run:
            output.append(lumi)
        else:
            yield (current_run, output)
            output = [lumi]
        current_run = run
    yield (current_run, output)

def collapse_ranges_in_list(xs):
    '''
    Generate a list of contiguous ranges in a list of numbers.
    Example:
    >>> list(collapse_ranges_in_list([1, 2, 3, 5, 8, 9, 10]))
    [[1, 3], [5, 5], [8, 10]]
    '''
    output = []
    for x in xs:
        if not output:
            # Starting new range
            output = [x, x]
        elif x == output[1]+1:
            output[1] = x
        else:
            yield output
            output = [x, x]
    yield output

def json_summary(run_lumi_set):
    '''
    Compute a crab -report like json summary for a set of runs and lumis.
    Example:
    >>> run_lumis = [(100, 2), (100, 1), (150, 1), (150, 2), (150, 8)]
    >>> # Disable indentation
    >>> json_summary(run_lumis)
    {'150': [[1, 2], [8, 8]], '100': [[1, 2]]}
    '''
    run_lumis = sorted(run_lumi_set)
    output = {}
    if not run_lumis:
        return output
    for run, lumis_in_run in group_by_run(run_lumis):
        output[str(run)] = list(collapse_ranges_in_list(lumis_in_run))
    return output

def lumi_list(lumimask, first=None, last=None):
    '''
    Convert a json-style lumimask to a plain set of (run, lumi)s.
    '''
    output = set([])
    for run, lumis in lumimask.iteritems():
        run = int(run)
        if first is not None and run < first:
            continue
        if last is not None and run > last:
            continue
        for lumirange in lumis:
            for lumi in range(lumirange[0], lumirange[1] + 1):
                output.add( (run, lumi) )
    return output

def lumi_list_from_file(filepath):
    '''
    Read a lumi mask from a json file and convert to to a set of run, lumis.
    If filepath is of the form file:first:last then only take runs between first
    and last.
    '''
    path = filepath
    first = None
    last = None
    if ':' in filepath:
        path, first, last = tuple(filepath.split(':'))
        first = int(first)
        last = int(last)
    result = None
    with open(path, 'r') as file:
        result = lumi_list(json.load(file), first, last)
    return result

if __name__ == "__main__":
    import doctest; doctest.testmod()