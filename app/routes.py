from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app.blockchain_nft import BlockchainNFT
from app.ipfs_service import IPFSService
from datetime import datetime

bp = Blueprint('main', __name__)

# Liste des étudiants en mémoire (temporaire)
etudiants = []

def allowed_file(filename):
    """Vérifie si le fichier est un PDF"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@bp.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@bp.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    """Page d'ajout de diplôme avec création de NFT"""
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            nom = request.form.get('nom')
            prenom = request.form.get('prenom')
            email = request.form.get('email')
            wallet_address = request.form.get('wallet_address')
            diplome = request.form.get('diplome')
            specialite = request.form.get('specialite')
            institution = request.form.get('institution', 'Université')
            
            # Validation des champs requis
            if not all([nom, prenom, email, wallet_address, diplome, specialite]):
                return jsonify({
                    'success': False,
                    'error': 'Tous les champs sont requis'
                }), 400
            
            # Vérifier le fichier PDF
            if 'diplome_pdf' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'Aucun fichier fourni'
                }), 400
            
            file = request.files['diplome_pdf']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'Aucun fichier sélectionné'
                }), 400
            
            if not allowed_file(file.filename):
                return jsonify({
                    'success': False,
                    'error': 'Seuls les fichiers PDF sont acceptés'
                }), 400
            
            # Sauvegarder le fichier temporairement
            filename = secure_filename(f"{nom}_{prenom}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # 1. Upload du PDF sur IPFS via Pinata
            ipfs_service = IPFSService(
                current_app.config['PINATA_API_KEY'],
                current_app.config['PINATA_SECRET_KEY'],
                current_app.config['PINATA_JWT']
            )
            
            pdf_result = ipfs_service.upload_file(filepath, filename)
            if not pdf_result['success']:
                os.remove(filepath)
                return jsonify({
                    'success': False,
                    'error': f"Échec de l'upload IPFS: {pdf_result.get('error', 'Erreur inconnue')}"
                }), 500
            
            # 2. Créer les métadonnées NFT
            metadata = {
                'name': f"Diplôme {diplome} - {nom} {prenom}",
                'description': f"Diplôme de {diplome} en {specialite} délivré à {nom} {prenom}",
                'image': pdf_result['url'],
                'attributes': [
                    {'trait_type': 'Nom', 'value': nom},
                    {'trait_type': 'Prénom', 'value': prenom},
                    {'trait_type': 'Email', 'value': email},
                    {'trait_type': 'Diplôme', 'value': diplome},
                    {'trait_type': 'Spécialité', 'value': specialite},
                    {'trait_type': 'Institution', 'value': institution},
                    {'trait_type': "Date d'émission", 'value': datetime.now().strftime('%Y-%m-%d')}
                ],
                'external_url': pdf_result['url']
            }
            
            # 3. Upload des métadonnées sur IPFS
            metadata_result = ipfs_service.upload_metadata(metadata)
            if not metadata_result['success']:
                os.remove(filepath)
                return jsonify({
                    'success': False,
                    'error': f"Échec de l'upload des métadonnées: {metadata_result.get('error', 'Erreur inconnue')}"
                }), 500
            
            # 4. Minter le NFT sur la blockchain
            blockchain = BlockchainNFT({
                'RPC_URL': current_app.config['RPC_URL'],
                'CONTRACT_ADDRESS': current_app.config['CONTRACT_ADDRESS'],
                'OWNER_PRIVATE_KEY': current_app.config['OWNER_PRIVATE_KEY'],
                'CHAIN_ID': current_app.config['CHAIN_ID']
            })
            
            mint_result = blockchain.mint_diploma(
                wallet_address,
                metadata_result['url'],
                f"{nom} {prenom}",
                f"{diplome} - {specialite}",
                institution
            )
            
            # Nettoyer le fichier temporaire
            if os.path.exists(filepath):
                os.remove(filepath)
            
            if mint_result['success']:
                # Ajouter l'étudiant à la liste
                etudiant = {
                    'nom': nom,
                    'prenom': prenom,
                    'email': email,
                    'wallet_address': wallet_address,
                    'diplome': diplome,
                    'specialite': specialite,
                    'institution': institution,
                    'nft_token_id': mint_result['token_id'],
                    'tx_hash': mint_result['tx_hash'],
                    'ipfs_url': pdf_result['url'],
                    'metadata_url': metadata_result['url'],
                    'date_ajout': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                etudiants.append(etudiant)
                
                return jsonify({
                    'success': True,
                    'message': 'NFT créé et envoyé avec succès!',
                    'data': etudiant
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': mint_result.get('error', 'Erreur lors du minting')
                }), 500
        
        except Exception as e:
            # Nettoyer le fichier en cas d'erreur
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({
                'success': False,
                'error': f'Erreur serveur: {str(e)}'
            }), 500
    
    # GET request
    return render_template('ajouter.html')

@bp.route('/liste')
def liste():
    """Page de liste des diplômes"""
    return render_template('liste.html', etudiants=etudiants)

@bp.route('/api/etudiants')
def get_etudiants():
    """API pour récupérer la liste des étudiants"""
    return jsonify({
        'success': True,
        'etudiants': etudiants
    })

@bp.route('/api/contract-info')
def contract_info():
    """API pour récupérer les informations du contrat"""
    try:
        blockchain = BlockchainNFT({
            'RPC_URL': current_app.config['RPC_URL'],
            'CONTRACT_ADDRESS': current_app.config['CONTRACT_ADDRESS'],
            'OWNER_PRIVATE_KEY': current_app.config['OWNER_PRIVATE_KEY'],
            'CHAIN_ID': current_app.config['CHAIN_ID']
        })
        
        total = blockchain.total_supply()
        
        return jsonify({
            'success': True,
            'contract_address': current_app.config['CONTRACT_ADDRESS'],
            'total_supply': total,
            'network': 'Polygon Amoy Testnet',
            'chain_id': current_app.config['CHAIN_ID']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/diploma/<int:token_id>')
def get_diploma_info(token_id):
    """API pour récupérer les informations d'un diplôme spécifique"""
    try:
        blockchain = BlockchainNFT({
            'RPC_URL': current_app.config['RPC_URL'],
            'CONTRACT_ADDRESS': current_app.config['CONTRACT_ADDRESS'],
            'OWNER_PRIVATE_KEY': current_app.config['OWNER_PRIVATE_KEY'],
            'CHAIN_ID': current_app.config['CHAIN_ID']
        })
        
        info = blockchain.get_diploma_info(token_id)
        
        if info['success']:
            return jsonify({
                'success': True,
                'data': info
            })
        else:
            return jsonify({
                'success': False,
                'error': info.get('error', 'Token introuvable')
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/health')
def health():
    """Endpoint de santé pour vérifier que l'API fonctionne"""
    return jsonify({
        'status': 'ok',
        'message': 'API Diplômes NFT opérationnelle'
    })
