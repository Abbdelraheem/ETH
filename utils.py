import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv(dotenv_path="private_key.env")

def load_wallet():
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        raise Exception("PRIVATE_KEY not found in environment!")
    wallet = Web3().eth.account.from_key(private_key)
    return wallet.address, private_key

def is_safe_contract(address):
    try:
        bytecode = Web3().eth.get_code(address).hex()
        return "636c61696d" in bytecode  # 'claim' in hex
    except:
        return False