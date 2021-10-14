import pandas as pd
df = pd.read_csv('sample_data.tsv', sep='\t')

# item_obj stores information related to each item, such as count, support, transaction ID (as a set)
item_obj = {}

transaction_count = df.shape[0]
min_support = 0.5
min_confidence = 0.7

for index, row in df.iterrows():
    record = row['Transaction']
    tid = row['Transaction']
    
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
            item_obj[item]['tranx_id'].add(tid)
        else:
            # creating an object in the dictionary for the first time
            item_obj[item] = {'cnt': 1}
            item_obj[item] = {'tranx_id': {tid}}
    
# calculating the support for each item
for key in item_obj:
    item_obj[key]['support'] = (item_obj[key]['cnt'])/transaction_count
