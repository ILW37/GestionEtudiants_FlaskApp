from web3 import Web3
import os

url = os.getenv("ALCHEMY_API_URL")
print("URL =", url)

w3 = Web3(Web3.HTTPProvider(url))
print("Web3 connecté :", w3.is_connected())

if w3.is_connected():
    print("Chaîne ID :", w3.eth.chain_id)
