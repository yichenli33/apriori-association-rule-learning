import sys
import argparse
from itertools import combinations
from itertools import permutations
from itertools import product
import csv


parser = argparse.ArgumentParser(description='process some arguments')
parser.add_argument('input')
parser.add_argument('output')
parser.add_argument('support', type=float)
parser.add_argument('conf', type=float)
args = parser.parse_args()
input_file = args.input
outputName = args.output
min_support_percentage = args.support
min_confidence = args.conf

contents = []
with open(input_file) as f:
    for line in f:
        no_new = line[:-1]
        clean_line = no_new.split(',')
        clean_line.pop(0)
        contents.append(clean_line)


'''contents: list of all transactions'''

num_total_transactions = len(contents)

''' items_dict a dict of item appearance'''
index = 1
items_dict = {}
for each_list in contents:

    for each_item in each_list:
        if each_item not in items_dict:
            items_dict.update({each_item: [index]})
        else:
            index_list = items_dict[each_item]
            index_list.append(index)
            items_dict.update({each_item: index_list})
    index += 1

'''get rid of item < min_support'''
''' i = 1 '''
vfi = {}
freq_combinations = []
freq_combinations.append([])
for item in items_dict:
    if len(items_dict.get(item))/num_total_transactions >= min_support_percentage:
        vfi.update({item:len(items_dict.get(item))/num_total_transactions})
        freq_combinations[0].append(item)


singles = sorted(freq_combinations[0])
i = 2
outputFile = '%s.sup=%s,conf=%s.csv' % (outputName[:-4], min_support_percentage, min_confidence)
with open(outputFile, 'w') as csvfile:
    outputwriter = csv.writer(csvfile, quoting=csv.QUOTE_NONE, escapechar=' ')
    vfi_list = sorted(vfi)

    '''single item >= min support'''
    for each in vfi_list:
        outputwriter.writerow(['S'] + ['%.4f' % vfi.get(each)] + [each])

    '''larger than 1-item pairs'''
    while len(list(combinations(singles, i))) is not 0:
        current_combos = list(combinations(singles, i))
        freq_combinations.append([])
        for each_tuple in current_combos:
            tmp_list = items_dict.get(each_tuple[0])
            for each_item in each_tuple:
                if each_item is each_tuple[0]:
                    continue
                else:
                    curr_list = items_dict.get(each_item)
                    tmp_list = list(set(tmp_list) & set(curr_list))
            support = len(tmp_list)/num_total_transactions
            if support >= min_support_percentage:
                freq_combinations[i-1].append(list(each_tuple))
                vfi.update({"".join(list(each_tuple)): support})
                outputwriter.writerow(['S'] + ['%.4f'%support] + list(each_tuple))
        i += 1

    '''all possible association rules in frequent item sets'''
    index = 1
    while len(freq_combinations[index]) is not 0:
        for each_comb in freq_combinations[index]:
            l1 = []
            l2 = []
            for pattern in product([True, False], repeat=len(each_comb)):
                l1.append([x[1] for x in zip(pattern, each_comb) if x[0]])
                l2.append([x[1] for x in zip(pattern, each_comb) if not x[0]])
            l1.pop(0)
            l1.pop()
            l2.pop(0)
            l2.pop()

            for idx, each in enumerate(l1):
                item = "".join(each)
                sup_small = vfi.get(item)
                sup_large = vfi.get("".join(each_comb))
                conf = sup_large/sup_small
                if conf >= min_confidence:

                    outputwriter.writerow(['R'] + ['%.4f'%sup_large] + ['%.4f'%conf] + each + ['=>'] + l2[idx])

        index += 1
