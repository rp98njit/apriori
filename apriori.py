import itertools
from pprint import pprint
import pandas as pd

df = pd.read_csv('sample_data.tsv', sep='\t')

# item_obj stores information related to each item, such as count, support, transaction ID (as a set)
item_obj = {}

transaction_count = df.shape[0]
min_support = 0.5
min_confidence = 0.7

'''
support_index stores item/items whose support is greater than or equal to min_support
Ex: support_index = {'1': ['item1'], '2': [(item1, item2), (item3, item4)]}
where key is the level in the steps
'''
support_index: dict = {1: []}
current_list_level = 1


def init_one():
    # creating the first level
    for index, row in df.iterrows():
        record = row['Transaction']
        tid = row['TID']

        # splitting each item
        items = record.split(',')
        # removing trailing spaces, lines for each item and converting it to lower case
        items = [item.lower().strip() for item in items]
        # removing duplicate items
        items = list(set(items))
        for item in items:
            if item in item_obj:
                # updating the existing object in the dictionary
                item_obj[item]['cnt'] = item_obj[item]['cnt'] + 1
                item_obj[item]['transactions'].add(tid)
            else:
                # creating an object in the dictionary for the first time
                item_obj[item] = {'cnt': 1, 'transactions': {tid}}
            # calculating the support
            item_obj[item]['support'] = (item_obj[item]['cnt']) / transaction_count
            # check minimum support
            if item_obj[item]['support'] >= min_support:
                if 1 in support_index and item not in support_index[1]:
                    support_index[1].append(item)
            else:
                if 1 in support_index and item in support_index[1]:
                    support_index[1].remove(item)


def next_step():
    global current_list_level
    current_support_items = support_index[1]
    # create combinations from previous level
    item_combinations = list(itertools.combinations(support_index[1], 2))

    while len(current_support_items) > 0:
        current_list_level += 1
        item_combinations = list(itertools.combinations(current_support_items,
                                                        current_list_level))
        current_support_items = []
        for combination in item_combinations:
            combination = tuple(sorted(combination))
            common_transactions = set(item_obj[combination[0]]['transactions'])
            for i in range(len(combination)-1):
                set_2 = set(item_obj[combination[i+1]]['transactions'])
                common_transactions = common_transactions.intersection(set_2)
            current_support = len(common_transactions)/transaction_count
            if current_support >= min_support:
                if current_list_level not in support_index:
                    support_index.update({current_list_level: [combination]})
                else:
                    support_index[current_list_level].extend([combination])
                current_support_items += list(combination)
                current_support_items = list(set(current_support_items))
                item_obj.update({combination: {'cnt': 1, 'transactions': common_transactions,
                                               'support': current_support}})


if __name__ == '__main__':
    init_one()
    next_step()
