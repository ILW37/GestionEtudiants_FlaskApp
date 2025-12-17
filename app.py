from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    print('=' * 60)
    print('🎓 Application Gestion Diplômes NFT')
    print('=' * 60)
    print(f'📍 URL locale: http://127.0.0.1:5000')
    print(f'🔗 Réseau: Polygon Amoy Testnet')
    print(f'📝 Contrat: {os.getenv("CONTRACT_ADDRESS", "Non configuré")}')
    print('=' * 60)
    print('')
    print('⚠️  Assurez-vous que:')
    print('  ✓ MetaMask est installé')
    print('  ✓ Vous êtes sur le réseau Polygon Amoy')
    print('  ✓ Vous avez des MATIC de test')
    print('')
    print('Appuyez sur CTRL+C pour arrêter le serveur')
    print('=' * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
