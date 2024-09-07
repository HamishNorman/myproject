import time, dotenv, os, pprint
import api_calls as api

#load .env variables
dotenv.load_dotenv()
dmarket_private = os.getenv("DMARKET_PRIVATE")
dmarket_public = os.getenv("DMARKET_PUBLIC")


def check_inventory():
    global dmarket_private, dmarket_public
    #request dmarket inventory
    items = api.get_dmarket_inventory(private_key=dmarket_private, public_key=dmarket_public)
    #if not empty: go through each item
    for i in items['Items']:
        #check item price based on title
        i_price = api.market_items(private_key=dmarket_private, public_key=dmarket_public, game_id='a8db', title=i['Title'], limit=1)
        #create json body for the item
        offer = {
            'Offers': [{
                'AssetID': i['AssetID'],
                'Price': {
                    'Currency': "USD",
                    'Amount': round(float(i_price['objects'][0]['price']['USD']) - 1,2)/100
                }
            }]
        }
        #list item on sale for 1 cent cheaper than cheapest offer
        response = api.post_offer(private_key=dmarket_private, public_key=dmarket_public, item=offer)
        if response['Result'][0]['Error'] == None:
            print(f'Successfully updated price for {i["Title"]} | ${response["Result"][0]["CreateOffer"]["Price"]["Amount"]}')
        else:
            pprint.pprint(response)
        #wait 1 second to not get caught by rate limit
        time.sleep(1)


def price_check():
    global dmarket_public, dmarket_private
    #request all listings
    listings = api.user_offers(private_key=dmarket_private, public_key=dmarket_public)
    #go through each listed item
    for l in listings['Items']:
        print(f'Checking price for {l["Title"]} ({l["Offer"]["Price"]["Amount"]})')
        #check if its lowest price
        cheapest_listing = api.market_items(private_key=dmarket_private, public_key=dmarket_public, game_id="a8db", title=l['Title'], limit=1)
        print(float(cheapest_listing['objects'][0]['price']['USD'])/100)
        if (float(cheapest_listing['objects'][0]['price']['USD'])/100) < float(l['Offer']['Price']['Amount']):
            #create a new json body with updated price
            updated_listing = {"Offers": 
                            [
                                {"OfferID": l['Offer']['OfferID'],
                                "AssetID": l['AssetID'],
                                "Price": {
                                    "Currency": 'USD',
                                    "Amount": round(float(cheapest_listing['objects'][0]['price']['USD']) - 1, 2)/100
                                    }
                                }
                            ]
                        }
            #update listing
            response = api.edit_offer(private_key=dmarket_private, public_key=dmarket_public, item=updated_listing)
            if response['Result'][0]['Error'] == None:
                print(f'Successfully updated price for {l["Title"]} | ${response["Result"][0]["EditOffer"]["Price"]["Amount"]}')
            else:
                pprint.pprint(response)
        #wait 1 second to not get caught by rate limit
        time.sleep(1)

# LOOP PROCESS
def loop():
    # loop starts
    while True:
        try:
            # check for listed items prices
            price_check()
            # if any pf them are not cheapest: undercut by 0.01 usd
            # checking for items in dmarket inventory
            check_inventory()
            # if any: list them for cheapest price
            # wait 16 minutes
            time.sleep(960)
        except Exception as e:
            #if error, print error message and exit
            print(e.with_traceback())
            exit(1)


if __name__ == "__main__":
    loop()