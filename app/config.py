import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10485760))
    
    # Blockchain
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
    OWNER_PRIVATE_KEY = os.getenv('OWNER_PRIVATE_KEY')
    RPC_URL = os.getenv('RPC_URL', 'https://rpc-amoy.polygon.technology/')
    CHAIN_ID = int(os.getenv('CHAIN_ID', 80002))
    
    # IPFS/Pinata
    PINATA_API_KEY = os.getenv('PINATA_API_KEY')
    PINATA_SECRET_KEY = os.getenv('PINATA_SECRET_KEY')
    PINATA_JWT = os.getenv('PINATA_JWT')
