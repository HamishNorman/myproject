import requests, json, json, logging
from datetime import datetime
from nacl.bindings import crypto_sign
from furl import furl



def header_creator_params( private_key, public_key, request_method: str, api_url: str, params: dict = None,):
    '''Creates request crypto sign header to authorize request. Use for endpoint requests or requests with params'''
    nonce = str(round(datetime.now().timestamp()))
    string_to_sign = request_method + api_url
    if params:
        string_to_sign = str(furl(string_to_sign).add(params))
    string_to_sign += nonce
    signature_prefix = "dmar ed25519 "
    encoded = string_to_sign.encode('utf-8')
    signature_bytes = crypto_sign(encoded, bytes.fromhex(private_key))
    signature = signature_bytes[:64].hex()
    headers = {
        "X-Request-Sign": signature_prefix + signature,
        "X-Api-Key": public_key,
        "X-Sign-Date": nonce,
        "Content-Type": "application/json"
        }
    return headers



def header_creator_body(private_key, public_key, request_method: str, api_url: str, body: dict):
    '''Creates request crypto sign header to authorize request. Use for requests with json body'''
    nonce = str(round(datetime.now().timestamp()))
    string_to_sign = request_method + api_url + json.dumps(body) + nonce
    signature_prefix = "dmar ed25519 "
    encoded = string_to_sign.encode('utf-8')
    signature_bytes = crypto_sign(encoded, bytes.fromhex(private_key))
    signature = signature_bytes[:64].hex()
    headers = {
        "X-Request-Sign": signature_prefix + signature,
        "X-Api-Key": public_key,
        "X-Sign-Date": nonce,
        "Content-Type": "application/json"
        }
    return headers


def get_dmarket_inventory(private_key, public_key) -> list:
    '''Returns items from dmarket inventory'''
    rootApiUrl = "https://api.dmarket.com"
    api_url = "/marketplace-api/v1/user-inventory"
    request_method = "GET"
    params = {
            "gameId": "a8db",
            "BasicFilters.InMarket": True,
            "Presentation": "InventoryPresentationDetailed",
            "Limit": 100
            }
    headers = header_creator_params(private_key, public_key, request_method, api_url, params)
    resp = requests.get(rootApiUrl + api_url, params=params, headers=headers)
    if resp.status_code == 200:
        logging.debug(f"GET DMARKET INVENTORY STATUS CODE - {resp.status_code}")
    else:
        logging.error(f"GET DMARKET INVENTORY STATUS CODE - {resp.status_code}")
    details = json.loads(resp.text)
    return details


def market_items(private_key, public_key, game_id, title: str = None, limit: float = 10) -> list:
    '''Returns cheapest listings for specific item'''
    rootApiUrl = "https://api.dmarket.com"
    api_url = "/exchange/v1/market/items"
    request_method = "GET"
    params = {"gameId": game_id,
              "title": title,
              "limit": limit,
              "OrderBy": "price",
              "OrderDir": "asc",
              "currency": "USD"}
    headers = header_creator_params(private_key, public_key, request_method, api_url, params)
    resp = requests.get(rootApiUrl + api_url, params=params, headers=headers)
    if resp.status_code == 200:
        logging.debug(f"GET NEWEST LISTINGS - {resp.status_code}")
    else:
        logging.error(f"GET NEWEST LISTINGS - {resp.status_code}")
    details = json.loads(resp.text)
    return details


def post_offer(private_key, public_key, item: dict):
    '''Sends request to list an item for sale'''
    rootApiUrl = "https://api.dmarket.com"
    api_url = "/marketplace-api/v1/user-offers/create"
    request_method = "POST"
    body = item
    headers = header_creator_body(private_key, public_key, request_method, api_url, body)
    resp = requests.post(rootApiUrl + api_url, json=body, headers=headers)
    if resp.status_code == 200:
        logging.debug(f"POST OFFERS STATUS CODE - {resp.status_code}")
    else:
        logging.error(f"POST OFFERS STATUS CODE - {resp.status_code}")
    details = json.loads(resp.text)
    return details


def edit_offer(private_key, public_key, item: dict):
    '''Edits item on sale'''
    rootApiUrl = "https://api.dmarket.com"
    api_url = "/marketplace-api/v1/user-offers/edit"
    request_method = "POST"
    body = item
    headers = header_creator_body(private_key, public_key, request_method, api_url, body)
    resp = requests.post(rootApiUrl + api_url, json=body, headers=headers)
    if resp.status_code == 200:
        logging.debug(f"POST OFFERS STATUS CODE - {resp.status_code}")
    else:
        logging.error(f"POST OFFERS STATUS CODE - {resp.status_code}")
    details = json.loads(resp.text)
    return details


def user_offers(private_key, public_key) -> list:
    '''Returns list of active user offers'''
    rootApiUrl = "https://api.dmarket.com"
    api_url = "/marketplace-api/v1/user-offers"
    request_method = "GET"
    params = {'GameID': 'a8db',
              'Status': 'OfferStatusActive',
              'SortType': 'UserOffersSortTypeDateNewestFirst',
              'Limit': 100,
              'BasicFilters.Currency': 'USD'}
    headers = header_creator_params(private_key, public_key, request_method, api_url, params)
    resp = requests.get(rootApiUrl+api_url, params=params, headers=headers)
    if resp.status_code == 200:
        logging.debug(f"GET USER OFFERS STATUS CODE - {resp.status_code}")
    else:
        logging.error(f"GET USER OFFERS STATUS CODE - {resp.status_code}")
    details = json.loads(resp.text)
    return details