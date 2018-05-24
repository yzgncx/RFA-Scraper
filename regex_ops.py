# encoding: utf-8

import re
import csv
import copy

# aka Filter
#
def sift(data, field, regex):
    new_data = []
    for line in data:
        tmp = regex.search(line[field])
        if tmp:
            new_data.append(line)
    return new_data

def find_all(data, field, regex):
    new_data = []
    for line in data:
        hits = regex.findall(line[field])
        if hits: #nonempty list
            tmp = []
            for i in range(len(hits)):
                tmp.append(copy.deepcopy(line))
            for i,x in enumerate(hits):
                tmp[i][field] = x[0] # cause groups
            new_data += copy.deepcopy(tmp)
    return new_data
    
def get_data(f):
    with open(f) as csvfile:
        dr = csv.DictReader(csvfile)
        data = []
        for row in dr:
            data.append(row)
        return data

def ensure_unicode(v):
    if isinstance(v, str):
        v = v.decode('utf8')
    return unicode(v)  # convert anything not a string to unicode too
