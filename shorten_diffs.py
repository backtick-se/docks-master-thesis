from utils import load, dump
import numpy as np
import statistics
import re

plock = (
    'json', 'yaml', 'txt', 'yml'
)


def get_type(path):
    pattern = re.compile('a\/.*\.([a-z]*)$')

    try:
        filetype = pattern.match(path).group(1)
    except:
        filetype = ''

    return filetype


def quantiles(values, q=90):
    num_quants = 100//(100-q)
    quant = statistics.quantiles(values, n=num_quants)[-1]
    return quant


if __name__ == "__main__":
    data = load('data/big_data/scraped_diffs.pickle')

    lengths = []

    for pr in data.values():
        for diff in pr['diffs']:
            # path = diff.split('\n')[0].split(' ')[0]
            # file = path.split('/')[-1]

            # if 'lock' in file:
            #     print(file)

            lengths.append(len(diff))

    print(f'Mean: {np.mean(lengths)}')
    print(f'Q75: {quantiles(lengths, q=75)}')
    print(f'Q80: {quantiles(lengths, q=80)}')
    print(f'Q85: {quantiles(lengths, q=85)}')
    print(f'Q90: {quantiles(lengths, q=90)}')

    quan = quantiles(lengths, q=95)

    print(f'Q95: {quantiles(lengths, q=95)}')

    toolong = []

    for (rid, num), pr in data.items():
        for diff in pr['diffs']:
            path = diff.split('\n')[0].split(' ')[0]
            file = path.split('/')[-1]
            exte = get_type(path)

            if len(diff) > quan and exte in plock:
                print(path, exte)
                toolong.append(num)

    remove = set(toolong)
    newset = {}

    for (rid, num), value in data.items():
        if num not in remove:
            newset[(rid, num)] = value

    print(len(data))
    print(len(newset))
    dump(newset, 'data/big_data/scraped_diffs_q95.pickle')
