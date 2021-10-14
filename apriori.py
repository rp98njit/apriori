import pandas as pd
df = pd.read_csv('sample_data.tsv', sep='\t')

item_obj = {}
transaction_count = df.shape[0]
min_support = 0.5
min_confidence = 0.7

for record in df['Transaction']:
    # splitting each item
    items = record.split(',')
    # removing trailing spaces, lines for each item and converting it to lower case
    items = [item.lower().strip() for item in items]
    # removing duplicate items
    items = list(set(items))
    for item in items:
        if item in item_obj:
            item_obj[item]['count'] = item_obj[item]['count'] + 1
        else:
            item_obj[item] = {'count': 1}

for key in item_obj:
    item_obj[key]['support'] = (item_obj[key]['count'])/transaction_count

print('Hello')

