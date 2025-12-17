from web3 import Web3
import json
from pathlib import Path

class BlockchainNFT:
    """Gestionnaire de la blockchain pour les NFT diplômes"""

    def __init__(self, config):
        self.rpc_url = config['RPC_URL']
        self.contract_address = config['CONTRACT_ADDRESS']
        self.owner_private_key = config['OWNER_PRIVATE_KEY']
        self.chain_id = config['CHAIN_ID']

        # Connexion Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

        if not self.w3.is_connected():
            raise Exception("Impossible de se connecter au réseau Polygon Amoy (RPC).")

        # Charger ABI
        abi_path = Path(__file__).parent.parent / 'contracts' / 'DiplomaNFT_ABI.json'
        if abi_path.exists():
            with open(abi_path, 'r') as f:
                self.contract_abi = json.load(f)
        else:
            self.contract_abi = self._get_minimal_abi()

        # Initialisation du contrat
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.contract_address),
            abi=self.contract_abi
        )

        # Correction clé privée
        if not self.owner_private_key.startswith("0x"):
            self.owner_private_key = "0x" + self.owner_private_key

        self.owner_account = self.w3.eth.account.from_key(self.owner_private_key)

    # -------------------------------------------------------------------
    # ABI minimal fallback
    # -------------------------------------------------------------------
    def _get_minimal_abi(self):
        return [
            {
                "inputs": [
                    {"internalType": "address", "name": "studentAddress", "type": "address"},
                    {"internalType": "string", "name": "tokenURI", "type": "string"},
                    {"internalType": "string", "name": "studentName", "type": "string"},
                    {"internalType": "string", "name": "degreeType", "type": "string"},
                    {"internalType": "string", "name": "institution", "type": "string"}
                ],
                "name": "mintDiploma",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
                "name": "getDiplomaInfo",
                "outputs": [
                    {"internalType": "string", "name": "studentName", "type": "string"},
                    {"internalType": "string", "name": "degreeType", "type": "string"},
                    {"internalType": "string", "name": "institution", "type": "string"},
                    {"internalType": "uint256", "name": "issueDate", "type": "uint256"},
                    {"internalType": "bool", "name": "isValid", "type": "bool"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "internalType": "uint256", "name": "tokenId", "type": "uint256"},
                    {"indexed": True, "internalType": "address", "name": "student", "type": "address"},
                    {"indexed": False, "internalType": "string", "name": "studentName", "type": "string"}
                ],
                "name": "DiplomaMinted",
                "type": "event"
            }
        ]

    # -------------------------------------------------------------------
    # Mint NFT - VERSION CORRIGÉE
    # -------------------------------------------------------------------
    def mint_diploma(self, student_address, ipfs_uri, student_name, degree_type, institution):
        try:
            if not self.w3.is_address(student_address):
                return {'success': False, 'error': "Adresse étudiante invalide."}

            nonce = self.w3.eth.get_transaction_count(self.owner_account.address)

            # -------------------------------------------------------------------
            # EIP-1559 — FIX SPÉCIAL POLYGON AMOY
            # -------------------------------------------------------------------
            base_fee = self.w3.eth.gas_price  # ~30 Gwei
            min_priority_fee = self.w3.to_wei(30, "gwei")  # REQUIRED: >= 25 Gwei
            max_fee = base_fee + self.w3.to_wei(50, "gwei")  # Base + 50 Gwei

            # Construire la transaction
            tx = self.contract.functions.mintDiploma(
                Web3.to_checksum_address(student_address),
                ipfs_uri,
                student_name,
                degree_type,
                institution
            ).build_transaction({
                "from": self.owner_account.address,
                "nonce": nonce,
                "gas": 500000,
                "maxPriorityFeePerGas": min_priority_fee,
                "maxFeePerGas": max_fee,
                "chainId": self.chain_id
            })

            # SIGNER — Web3.py 6.x
            signed_txn = self.w3.eth.account.sign_transaction(tx, self.owner_private_key)

            # FIX CRITIQUE: Pour Web3.py 6.x, utilisez raw_transaction (pas rawTransaction)
            # Mais vérifier la version et utiliser la bonne propriété
            try:
                raw_tx = signed_txn.raw_transaction
            except AttributeError:
                raw_tx = signed_txn.rawTransaction
            
            tx_hash = self.w3.eth.send_raw_transaction(raw_tx)

            print(f"Transaction envoyée : {tx_hash.hex()}")
            print("⏳ Attente de confirmation...")

            # Augmenter le timeout à 300 secondes (5 minutes)
            try:
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
                print(f"✅ Transaction confirmée dans le bloc {receipt['blockNumber']}")
            except Exception as timeout_error:
                print(f"⚠️ Timeout d'attente, vérification du statut...")
                # Essayer de récupérer le receipt quand même
                try:
                    receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                    if not receipt:
                        return {
                            'success': False,
                            'error': f'Transaction envoyée mais pas encore confirmée. Vérifiez sur PolygonScan.',
                            'tx_hash': tx_hash.hex(),
                            'pending': True
                        }
                except:
                    return {
                        'success': False,
                        'error': f'Transaction envoyée mais confirmation impossible. Hash: {tx_hash.hex()}',
                        'tx_hash': tx_hash.hex(),
                        'pending': True
                    }

            # Vérifier le statut de la transaction
            if receipt['status'] != 1:
                return {
                    "success": False, 
                    "error": "Transaction échouée sur la blockchain", 
                    "tx_hash": tx_hash.hex()
                }

            # Lecture de l'événement DiplomaMinted
            token_id = None
            try:
                logs = self.contract.events.DiplomaMinted().process_receipt(receipt)
                if logs and len(logs) > 0:
                    token_id = logs[0]["args"]["tokenId"]
                    print(f"🎉 NFT créé avec Token ID: {token_id}")
            except Exception as e:
                print(f"⚠️ Impossible de décoder l'événement: {e}")
                # Fallback: utiliser totalSupply
                try:
                    token_id = max(self.total_supply() - 1, 0)
                except:
                    token_id = 0

            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "token_id": token_id,
                "gas_used": receipt['gasUsed'],
                "block_number": receipt['blockNumber']
            }

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Erreur lors de la création du NFT: {error_msg}")
            
            # Messages d'erreur plus explicites
            if 'insufficient funds' in error_msg.lower():
                error_msg = 'Fonds insuffisants pour payer les frais de gas. Obtenez des MATIC de test sur https://faucet.polygon.technology/'
            elif 'nonce too low' in error_msg.lower():
                error_msg = 'Erreur de nonce. Une transaction est peut-être en attente. Attendez quelques secondes.'
            elif 'replacement transaction underpriced' in error_msg.lower():
                error_msg = 'Transaction en attente. Attendez la confirmation de la transaction précédente.'
            elif 'execution reverted' in error_msg.lower():
                error_msg = 'Transaction rejetée par le contrat. Vérifiez que vous êtes le propriétaire du contrat.'
            
            return {"success": False, "error": error_msg}

    # -------------------------------------------------------------------
    def total_supply(self):
        try:
            return self.contract.functions.totalSupply().call()
        except Exception as e:
            print(f"Erreur totalSupply: {e}")
            return 0

    # -------------------------------------------------------------------
    def get_diploma_info(self, token_id):
        try:
            info = self.contract.functions.getDiplomaInfo(token_id).call()
            return {
                "success": True,
                "student_name": info[0],
                "degree_type": info[1],
                "institution": info[2],
                "issue_date": info[3],
                "is_valid": info[4]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # -------------------------------------------------------------------
    def get_balance(self, address):
        try:
            bal = self.w3.eth.get_balance(Web3.to_checksum_address(address))
            return float(self.w3.from_wei(bal, "ether"))
        except Exception as e:
            print(f"Erreur get_balance: {e}")
            return 0.0

    # -------------------------------------------------------------------
    def is_connected(self):
        return self.w3.is_connected()

    def get_network_info(self):
        try:
            return {
                "success": True,
                "chain_id": self.w3.eth.chain_id,
                "block_number": self.w3.eth.block_number,
                "gas_price_gwei": float(self.w3.from_wei(self.w3.eth.gas_price, "gwei")),
                "connected": True
            }
        except Exception as e:
            return {"success": False, "error": str(e), "connected": False}