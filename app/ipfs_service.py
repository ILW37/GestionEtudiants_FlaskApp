import requests
import json

class IPFSService:
    """Service de gestion IPFS via Pinata"""
    
    def __init__(self, api_key, secret_key, jwt):
        """
        Initialiser le service IPFS
        
        Args:
            api_key: Clé API Pinata
            secret_key: Clé secrète Pinata
            jwt: JWT Token Pinata
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.jwt = jwt
        self.pinata_api_url = 'https://api.pinata.cloud/pinning/pinFileToIPFS'
        self.pinata_json_url = 'https://api.pinata.cloud/pinning/pinJSONToIPFS'
        self.gateway_url = 'https://gateway.pinata.cloud/ipfs/'
    
    def upload_file(self, file_path, file_name):
        """
        Upload un fichier sur IPFS via Pinata
        
        Args:
            file_path: Chemin du fichier à uploader
            file_name: Nom du fichier
        
        Returns:
            dict: Résultat de l'upload
        """
        try:
            # Préparer les headers
            headers = {
                'Authorization': f'Bearer {self.jwt}'
            }
            
            # Ouvrir et uploader le fichier
            with open(file_path, 'rb') as f:
                files = {
                    'file': (file_name, f)
                }
                
                # Métadonnées optionnelles
                pinata_metadata = {
                    'name': file_name,
                    'keyvalues': {
                        'type': 'diploma',
                        'uploaded_at': str(int(__import__('time').time()))
                    }
                }
                
                data = {
                    'pinataMetadata': json.dumps(pinata_metadata),
                    'pinataOptions': json.dumps({
                        'cidVersion': 1
                    })
                }
                
                # Envoyer la requête
                response = requests.post(
                    self.pinata_api_url,
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=120  # 2 minutes timeout
                )
            
            # Vérifier la réponse
            if response.status_code == 200:
                result = response.json()
                ipfs_hash = result['IpfsHash']
                
                return {
                    'success': True,
                    'ipfs_hash': ipfs_hash,
                    'url': f'{self.gateway_url}{ipfs_hash}',
                    'size': result.get('PinSize', 0),
                    'timestamp': result.get('Timestamp', '')
                }
            else:
                error_message = response.text
                try:
                    error_json = response.json()
                    error_message = error_json.get('error', {}).get('details', error_message)
                except:
                    pass
                
                return {
                    'success': False,
                    'error': f'Erreur Pinata ({response.status_code}): {error_message}'
                }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Timeout lors de l\'upload sur IPFS. Le fichier est peut-être trop volumineux.'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Erreur de connexion à Pinata: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur lors de l\'upload du fichier: {str(e)}'
            }
    
    def upload_metadata(self, metadata):
        """
        Upload des métadonnées JSON sur IPFS via Pinata
        
        Args:
            metadata: Dictionnaire de métadonnées
        
        Returns:
            dict: Résultat de l'upload
        """
        try:
            # Préparer les headers
            headers = {
                'Authorization': f'Bearer {self.jwt}',
                'Content-Type': 'application/json'
            }
            
            # Préparer les données
            data = {
                'pinataContent': metadata,
                'pinataMetadata': {
                    'name': f"metadata_{metadata.get('name', 'unknown')}",
                    'keyvalues': {
                        'type': 'diploma_metadata',
                        'student': metadata.get('name', ''),
                        'uploaded_at': str(int(__import__('time').time()))
                    }
                },
                'pinataOptions': {
                    'cidVersion': 1
                }
            }
            
            # Envoyer la requête
            response = requests.post(
                self.pinata_json_url,
                json=data,
                headers=headers,
                timeout=60
            )
            
            # Vérifier la réponse
            if response.status_code == 200:
                result = response.json()
                ipfs_hash = result['IpfsHash']
                
                return {
                    'success': True,
                    'ipfs_hash': ipfs_hash,
                    'url': f'{self.gateway_url}{ipfs_hash}',
                    'size': result.get('PinSize', 0),
                    'timestamp': result.get('Timestamp', '')
                }
            else:
                error_message = response.text
                try:
                    error_json = response.json()
                    error_message = error_json.get('error', {}).get('details', error_message)
                except:
                    pass
                
                return {
                    'success': False,
                    'error': f'Erreur Pinata ({response.status_code}): {error_message}'
                }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Timeout lors de l\'upload des métadonnées sur IPFS.'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Erreur de connexion à Pinata: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur lors de l\'upload des métadonnées: {str(e)}'
            }
    
    def get_file_info(self, ipfs_hash):
        """
        Récupérer les informations d'un fichier sur IPFS
        
        Args:
            ipfs_hash: Hash IPFS du fichier
        
        Returns:
            dict: Informations du fichier
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.jwt}'
            }
            
            response = requests.get(
                f'https://api.pinata.cloud/data/pinList?hashContains={ipfs_hash}',
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['count'] > 0:
                    pin_info = result['rows'][0]
                    return {
                        'success': True,
                        'ipfs_hash': pin_info['ipfs_pin_hash'],
                        'size': pin_info['size'],
                        'timestamp': pin_info['date_pinned'],
                        'name': pin_info.get('metadata', {}).get('name', '')
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Fichier non trouvé sur IPFS'
                    }
            else:
                return {
                    'success': False,
                    'error': f'Erreur lors de la récupération des informations: {response.status_code}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def unpin_file(self, ipfs_hash):
        """
        Supprimer un fichier d'IPFS (unpin)
        
        Args:
            ipfs_hash: Hash IPFS du fichier
        
        Returns:
            dict: Résultat de l'opération
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.jwt}'
            }
            
            response = requests.delete(
                f'https://api.pinata.cloud/pinning/unpin/{ipfs_hash}',
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': f'Fichier {ipfs_hash} supprimé avec succès'
                }
            else:
                return {
                    'success': False,
                    'error': f'Erreur lors de la suppression: {response.status_code}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_connection(self):
        """
        Tester la connexion à Pinata
        
        Returns:
            dict: Résultat du test
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.jwt}'
            }
            
            response = requests.get(
                'https://api.pinata.cloud/data/testAuthentication',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'message': result.get('message', 'Connexion réussie'),
                    'authenticated': True
                }
            else:
                return {
                    'success': False,
                    'error': f'Échec de l\'authentification ({response.status_code})',
                    'authenticated': False
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur de connexion: {str(e)}',
                'authenticated': False
            }
    
    def get_pinata_usage(self):
        """
        Obtenir les statistiques d'utilisation Pinata
        
        Returns:
            dict: Statistiques d'utilisation
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.jwt}'
            }
            
            response = requests.get(
                'https://api.pinata.cloud/data/userPinnedDataTotal',
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'pin_count': result.get('pin_count', 0),
                    'pin_size_total': result.get('pin_size_total', 0),
                    'pin_size_with_replications_total': result.get('pin_size_with_replications_total', 0)
                }
            else:
                return {
                    'success': False,
                    'error': f'Erreur lors de la récupération des statistiques: {response.status_code}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }# PLACEHOLDER - Voir le guide complet pour le contenu
# Ce fichier doit être créé manuellement ou copié depuis le guide
