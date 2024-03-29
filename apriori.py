import itertools

try:
    import pandas as pd
except ModuleNotFoundError as e:
    print('-----ERROR-----')
    print("Pandas library is not installed. Execute 'pip install pandas==1.3.4'.\n\
If faced with errors drop an email to rp98@njit.edu or rajendra7406@gmail.com")
    exit(0)

try:
    from apyori import apriori
except ModuleNotFoundError():
    print('-----ERROR-----')
    print("Pandas library is not installed. Execute 'pip install apyori==1.1.2'.\n\
If faced with errors drop an email to rp98@njit.edu or rajendra7406@gmail.com")
    exit(0)

print('*' * 100)
print('This an implementation of apriori alogorithm from scratch.\n\
Choose the dataset ID to continue further.')
print('*' * 100)

print('\n\
ID Dataset\n\
1  Amazon\n\
2  Best Buy\n\
3  Custom Data\n\
4  General Data\n\
5  Kmart\n\
6  Nike\n\
7  Sample Data\n')

dataset_id = 1
while 1:
    try:
        dataset_id = int(input('Enter the ID of dataset: '))
    except ValueError as e:
        print('Enter a value from one of the IDs')
        continue
    if 1 <= dataset_id <= 7:
        break
    else:
        print('Enter a value from one of the IDs')
        continue

dataset_id_mapping = {1: 'amazon.tsv', 2: 'best_buy.tsv', 3: 'custom_data.tsv', 4: 'general.tsv', 5: 'kmart.tsv',
                      6: 'nike.tsv', 7: 'sample_data.tsv'}

df = pd.read_csv(dataset_id_mapping[dataset_id], sep='\t')

# item_obj stores information related to each item, such as count, support, transaction ID (as a set)
item_obj = {}

transaction_count = df.shape[0]

min_support = 0.5
while 1:
    try:
        min_support = float(input('\nEnter minimum support (value should be between 0.01 and 0.99): '))
    except ValueError as e:
        print('Enter a decimal value between 0.01 and 0.99')
        continue
    if 0.01 <= min_support <= 0.99:
        break
    else:
        print('Enter a decimal value between 0.01 and 0.99')
        continue

min_confidence = 0.5
while 1:
    try:
        min_confidence = float(input('\nEnter minimum confidence (value should be between 0.01 and 0.99): '))
    except ValueError as e:
        print('Enter a decimal value between 0.01 and 0.99')
        continue
    if 0.01 <= min_confidence <= 0.99:
        break
    else:
        print('Enter a decimal value between 0.01 and 0.99')
        continue

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
            for i in range(len(combination) - 1):
                set_2 = set(item_obj[combination[i + 1]]['transactions'])
                common_transactions = common_transactions.intersection(set_2)
            current_support = len(common_transactions) / transaction_count
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

        for i in range(1, 2 ** len(item) - 1):
            right_side = []
            indexes = '{0:b}'.format(i)
            indexes = '0' * (len(item) - len(indexes)) + indexes

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

    return association_rules


def apriori_by_library():
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


def output_program():
    print('-' * 100)
    print('Item frequent sets from my program')
    change_in_type = 1
    print('1 item frequency set')
    for key1 in item_obj.keys():
        if type(key1) is str:
            print(key1)
        else:
            if change_in_type != len(key1):
                change_in_type = len(key1)
                print('\n{}-item frequency set'.format(len(key1)))
                print(str(key1))
            else:
                print(str(key1))


if __name__ == '__main__':
    init_one()
    a = next_step()
    b = apriori_by_library()
    output_program()

    print('-'*100)
    print('Association rules are as follows: ')
    for key in a:
        for each_recommendation in a[key]:
            print('{} -> {}'.format(key, each_recommendation['recommendations']))

    print('-' * 100)
    print('Association Rules from library')
    for key in b:
        for each_recommendation in b[key]:
            print('{} -> {}'.format(key, each_recommendation['recommendations']))
