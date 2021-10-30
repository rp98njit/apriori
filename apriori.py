import itertools
from pprint import pprint
from deepdiff import DeepDiff
import pandas as pd

df = pd.read_csv('nike.tsv', sep='\t')

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
        record = row[df.columns[1]]
        tid = row[df.columns[0]]

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

    for item in list(item_obj):
        support = (item_obj[item]['cnt']) / transaction_count
        if support < min_support:
            del item_obj[item]
        else:
            item_obj[item].update({'support': support})
            support_index[1].append(item)


def next_step():
    global current_list_level
    current_support_items = support_index[1]
    association_rules = {}

    while len(current_support_items) > 0:
        current_list_level += 1
        # create combinations from previous level
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

    for item in item_obj:
        if type(item) == str:
            continue

        for i in range(1, 2**len(item)-1):
            right_side = []
            indexes = '{0:b}'.format(i)
            indexes = '0'*(len(item)-len(indexes)) + indexes

            for j, value in enumerate(indexes):
                if value == '1':
                    right_side.append(item[j])
            left_side = [each_item for each_item in item if each_item not in right_side]
            if len(left_side) == 1:
                left_side = left_side[0]
            else:
                left_side = tuple(left_side)

            if len(right_side) == 1:
                right_side = right_side[0]
            else:
                right_side = tuple(right_side)

            confidence = item_obj[item]['support'] / item_obj[left_side]['support']
            if confidence < min_confidence:
                continue

            if left_side in association_rules:
                association_rules[left_side].append({'recommendations': right_side, 'confidence': confidence})
            else:
                association_rules.update({left_side: [{'recommendations': right_side, 'confidence': confidence}]})

    # pprint(item_obj)
    # print('-'*100)
    # pprint(association_rules)
    # print('Association rules are as follows: ')
    # for key in association_rules:
    #     for each_recommendation in association_rules[key]:
    #         print('{} -> {}'.format(key, each_recommendation['recommendations']))
    return association_rules


def apriori_by_library():
    from apyori import apriori
    records = []
    for each_row in df[df.columns[1]]:
        items = each_row.split(',')
        items = [item.lower().strip() for item in items]
        records.append(items)
        
    association_rules_by_library = apriori(records, min_support=min_support, min_confidence=min_confidence)
    association_rules_by_library = list(association_rules_by_library)
    bb = {}
    for each_rule in association_rules_by_library:
        for i in each_rule[2]:
            if len(list(i[0])) == 0:
                continue
            base = tuple(i[0])
            if len(base) == 1:
                base = base[0]
            else:
                base = tuple(sorted(base))
            recommendations = tuple(i[1])
            if len(recommendations) == 1:
                recommendations = recommendations[0]

            cc = {'confidence': i[2], 'recommendations': recommendations}
            if base in bb:
                bb[base].extend([cc])
            else:
                bb[base] = [cc]

    return bb


if __name__ == '__main__':
    init_one()
    a = next_step()
    b = apriori_by_library()
    print('Association Rules from my program')
    pprint(a)
    print('-'*100)
    print('Association Rules from library')
    pprint(b)