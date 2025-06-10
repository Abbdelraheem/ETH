from web3 import Web3
from utils import load_wallet

INFURA_URL = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
web3 = Web3(Web3.HTTPProvider(INFURA_URL))
wallet_address, private_key = load_wallet()

def claim_token(contract_address, status):
    try:
        contract = web3.eth.contract(address=contract_address, abi=[{
            "constant": False,
            "inputs": [],
            "name": "claim",
            "outputs": [],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function"
        }])
        
        nonce = web3.eth.get_transaction_count(wallet_address)
        tx = contract.functions.claim().build_transaction({
            'from': wallet_address,
            'gas': 150000,
            'gasPrice': web3.toWei('30', 'gwei'),
            'nonce': nonce
        })
        
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        status['stats']['successful_claims'] += 1
        status['activity_log'].append({
            'time': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            'message': f"تم المطالبة من {contract_address[:12]}...، TX: {web3.toHex(tx_hash)[:12]}...",
            'level': 'success'
        })
        
    except Exception as e:
        status['stats']['failed_claims'] += 1
        status['activity_log'].append({
            'time': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            'message': f"فشل المطالبة: {str(e)}",
            'level': 'error'
        })