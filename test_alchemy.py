from dotenv import load_dotenv
import os
from web3 import Web3
import requests

load_dotenv()

alchemy_url = os.getenv("ALCHEMY_API_URL")

print("====================================")
print("1️⃣  Test chargement .env")
print("====================================")
print("ALCHEMY_API_URL =", alchemy_url)

if not alchemy_url:
    print("\n❌ ERREUR : ALCHEMY_API_URL est vide ou introuvable dans .env")
    exit()

print("\n====================================")
print("2️⃣  Test requête HTTP directe à Alchemy")
print("====================================")

try:
    r = requests.get(alchemy_url)
    print("Code HTTP :", r.status_code)
except Exception as e:
    print("❌ Erreur HTTP :", e)

print("\n====================================")
print("3️⃣  Test connexion Web3")
print("====================================")

try:
    w3 = Web3(Web3.HTTPProvider(alchemy_url))
    print("Connexion Web3 :", w3.is_connected())
except Exception as e:
    print("❌ Erreur Web3 :", e)

print("\n====================================")
print("🟢 TEST TERMINÉ")
print("====================================")
