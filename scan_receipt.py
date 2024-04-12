import veryfi
import pprint

def scan_image(imag):

    cid='vrfYoTzAfW9K249J6x843jAh7xjH4VeH6vrbXCA'
    csecret='ttRPgWrOxDLpTpfpWC7DIH9ILAjZS42VUnAoODkvoI3T6Gd1k0Nu9roAo8Mc29O18YtLKN7KoLV5PpmJBFSkllkgvnL7ukb4XBYmyTEeEOImLd22Eoov14c3OXh82OfL'
    uname='ak.akshayajay'
    apikey='bcd7db559a7c130ef6ae542b1b90a5fd'
    client=veryfi.Client(cid,csecret,uname,apikey)
    jsondata=client.process_document(imag)
    #pprint.pprint(jsondata)
    total = jsondata.get('total', 'Total not found')
    category = jsondata.get('category', 'Category not found')
    return total,category

