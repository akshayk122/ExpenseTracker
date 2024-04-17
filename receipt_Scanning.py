import veryfi
import pprint
cid='vrfYoTzAfW9K249J6x843jAh7xjH4VeH6vrbXCA'
csecret='ttRPgWrOxDLpTpfpWC7DIH9ILAjZS42VUnAoODkvoI3T6Gd1k0Nu9roAo8Mc29O18YtLKN7KoLV5PpmJBFSkllkgvnL7ukb4XBYmyTEeEOImLd22Eoov14c3OXh82OfL'
uname='ak.akshayajay'
apikey='bcd7db559a7c130ef6ae542b1b90a5fd'

client=veryfi.Client(cid,csecret,uname,apikey)

jsondata=client.process_document(r'C:\Users\AKSHAY\Downloads\bill123.pdf')
#pprint.pprint(jsondata)
total = jsondata.get('total', 'Total not found')
category = jsondata.get('category', 'Category not found')
#print('Total',total)
#print('Category',category)
#print(jsondata)

bill_name = jsondata.get('document_title', 'Bill name not found')
print('Bill Name:', bill_name)

# Extract and print item names and their prices
items = jsondata.get('line_items', [])
for item in items:
    item_name = item.get('description', 'Item description not found')
    item_price = item.get('total', 'Price not found')
    print(f'Item: {item_name}, Price: {item_price}')   
total_amount = jsondata.get('total', 'Total amount not found')
tax_amount = jsondata.get('tax', 'Tax not found')
print('Total Amount:', total_amount)
print('Tax:', tax_amount)
print(jsondata)