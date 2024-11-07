from flask import render_template, request, jsonify
from web3 import Web3
import json
import os

from . import create_app

app = create_app()

# Load deployed contract
with open("contracts/deployed_contract.json") as f:
    contract_data = json.load(f)

contract_address = contract_data["address"]
contract_abi = contract_data["abi"]

# Connect to Base blockchain
w3 = Web3(Web3.HTTPProvider("https://base-mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"))

# Initialize contract
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# In-memory player data (consider using a database for production)
players = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/join', methods=['POST'])
def join_game():
    player_address = request.form.get('address')

    if not w3.isAddress(player_address):
        return jsonify({"message": "Invalid Ethereum address"}), 400

    if player_address in players:
        return jsonify({"message": "Player already joined"}), 400

    # Initialize player data
    players[player_address] = {
        "assets": [],
        "balance": 0
    }

    return jsonify({"message": "Player joined successfully"}), 200

@app.route('/collect', methods=['POST'])
def collect_item():
    player_address = request.form.get('address')
    item = request.form.get('item')

    if player_address not in players:
        return jsonify({"message": "Player not found"}), 404

    players[player_address]['assets'].append(item)
    return jsonify({"message": f"Collected item: {item}"}), 200

@app.route('/trade', methods=['POST'])
def trade_item():
    sender = request.form.get('sender')
    receiver = request.form.get('receiver')
    item = request.form.get('item')

    if sender not in players or receiver not in players:
        return jsonify({"message": "Sender or receiver not found"}), 404

    if item not in players[sender]['assets']:
        return jsonify({"message": "Sender does not own the item"}), 400

    players[sender]['assets'].remove(item)
    players[receiver]['assets'].append(item)

    return jsonify({"message": f"Traded item: {item} from {sender} to {receiver}"}), 200

@app.route('/mint', methods=['POST'])
def mint_nft():
    player_address = request.form.get('address')
    item = request.form.get('item')

    if player_address not in players:
        return jsonify({"message": "Player not found"}), 404

    # Example tokenURI, in practice generate dynamically or use metadata storage
    token_uri = f"https://example.com/metadata/{item}.json"

    # Build transaction
    nonce = w3.eth.getTransactionCount(player_address)
    txn = contract.functions.mintNFT(player_address, token_uri).buildTransaction({
        'from': player_address,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.toWei('50', 'gwei')
    })

    # Sign the transaction
    private_key = os.getenv("PRIVATE_KEY")  # Ensure to set your private key as an environment variable
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)

    # Send the transaction
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.waitForTransactionReceipt(txn_hash)

    # Update player assets
    players[player_address]['assets'].append(item)

    return jsonify({
        "message": f"Minted NFT: {item}",
        "transaction_hash": w3.toHex(txn_hash)
    }), 200
