from web3 import Web3
from solcx import compile_standard, install_solc
import json
import os

# Install Solidity compiler
install_solc('0.8.0')

# Read the Solidity contract
with open("contracts/CryptoQuest.sol", "r") as file:
    crypto_quest_file = file.read()

# Compile the contract
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "CryptoQuest.sol": {
            "content": crypto_quest_file
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
            }
        }
    }
}, solc_version="0.8.0")

# Save the compiled contract
with open("contracts/compiled_contract.json", "w") as file:
    json.dump(compiled_sol, file)

# Extract bytecode and ABI
bytecode = compiled_sol['contracts']['CryptoQuest.sol']['CryptoQuest']['evm']['bytecode']['object']
abi = compiled_sol['contracts']['CryptoQuest.sol']['CryptoQuest']['abi']

# Connect to Base blockchain (replace with your provider)
w3 = Web3(Web3.HTTPProvider("https://base-mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"))

# Set up account
private_key = "YOUR_PRIVATE_KEY"
account = w3.eth.account.from_key(private_key)
w3.eth.default_account = account.address

# Create contract in Python
CryptoQuest = w3.eth.contract(abi=abi, bytecode=bytecode)

# Submit the transaction
print("Deploying contract...")
tx = CryptoQuest.constructor().buildTransaction({
    'nonce': w3.eth.getTransactionCount(account.address),
    'gas': 500000,
    'gasPrice': w3.toWei('50', 'gwei')
})

# Sign the transaction
signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)

# Send the transaction
tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

print(f"Transaction hash: {w3.toHex(tx_hash)}")
print("Waiting for transaction receipt...")
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
print(f"Contract deployed at address: {tx_receipt.contractAddress}")

# Save the contract address and ABI for later use
contract_data = {
    "abi": abi,
    "address": tx_receipt.contractAddress
}

with open("contracts/deployed_contract.json", "w") as file:
    json.dump(contract_data, file)
