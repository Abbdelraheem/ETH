from web3 import Web3
from utils import is_safe_contract
from claimer import claim_token
import time
from datetime import datetime

INFURA_URL = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

def scan_blocks(stop_event, status):
    print("🔍 بدء مسح كتل الإيثيريوم...")
    latest = web3.eth.block_number
    status['last_scan_block'] = latest
    
    while not stop_event.is_set():
        try:
            current = web3.eth.block_number
            if current > status['last_scan_block']:
                block = web3.eth.get_block(status['last_scan_block'] + 1, full_transactions=True)
                
                for tx in block.transactions:
                    if tx.to and web3.eth.get_code(tx.to) != b'':
                        status['stats']['contracts_scanned'] += 1
                        
                        if is_safe_contract(tx.to):
                            status['activity_log'].append({
                                'time': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                                'message': f"عقد محتمل: {tx.to}",
                                'level': 'info'
                            })
                            claim_token(tx.to, status)
                
                status['last_scan_block'] = current
            time.sleep(5)
        except Exception as e:
            status['activity_log'].append({
                'time': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                'message': f"خطأ في المسح: {str(e)}",
                'level': 'error'
            })
            time.sleep(10)