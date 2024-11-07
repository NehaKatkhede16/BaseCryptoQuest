from flask import Flask, render_template, request, jsonify
from web3 import Web3

# Connect to Base blockchain
infura_url = "https://base-mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
w3 = Web3(Web3.HTTPProvider(infura_url))

# Check connection to blockchain
if w3.isConnected():
    print("Connected to Base blockchain")
else:
    print("Failed to connect to Base blockchain")

# Smart contract ABI and address (replace with your own)
contract_address = "0xYourContractAddress"
contract_abi = [
    # Your smart contract's ABI goes here
]

# Load the smart contract
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Flask app to create game interface
app = Flask(__name__)

# In-game player data (for demonstration purposes)
players = {}

@app.route('/')
def index():
    return render_template('index.html')  # Frontend of the game

# Route for player to join game
@app.route('/join', methods=['POST'])
def join_game():
    player_address = request.form['address']
    
    if player_address in players:
        return jsonify({"message": "Player already joined"})
    
    # Create a new player with empty assets
    players[player_address] = {
        "assets": [],
        "balance": 0
    }
    
    return jsonify({"message": "Player joined successfully"})

# Route for collecting in-game items (e.g., NFTs)
@app.route('/collect', methods=['POST'])
def collect_item():
    player_address = request.form['address']
    item = request.form['item']
    
    if player_address not in players:
        return jsonify({"message": "Player not found"})
    
    # Add item to player's assets
    players[player_address]['assets'].append(item)
    
    return jsonify({"message": f"Collected item: {item}"})

# Route for trading items between players
@app.route('/trade', methods=['POST'])
def trade_item():
    sender_address = request.form['sender']
    receiver_address = request.form['receiver']
    item = request.form['item']
    
    if sender_address not in players or receiver_address not in players:
        return jsonify({"message": "Sender or receiver not found"})
    
    # Check if sender has the item
    if item not in players[sender_address]['assets']:
        return jsonify({"message": "Sender does not have the item"})
    
    # Remove item from sender and add to receiver
    players[sender_address]['assets'].remove(item)
    players[receiver_address]['assets'].append(item)
    
    return jsonify({"message": f"Traded item: {item} from {sender_address} to {receiver_address}"})

# Route for interacting with blockchain (e.g., minting NFTs)
@app.route('/mint', methods=['POST'])
def mint_nft():
    player_address = request.form['address']
    item = request.form['item']
    
    if player_address not in players:
        return jsonify({"message": "Player not found"})
    
    # Transaction to mint an NFT
    nonce = w3.eth.getTransactionCount(player_address)
    transaction = contract.functions.mintNFT(player_address, item).buildTransaction({
        'nonce': nonce,
        'gas': 2000000,
        'gasPrice': w3.toWei('50', 'gwei')
    })
    
    # Sign the transaction (replace with actual private key handling)
    signed_txn = w3.eth.account.signTransaction(transaction, private_key="YourPrivateKey")
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    
    return jsonify({"message": f"Minted NFT: {item}", "transaction_hash": w3.toHex(txn_hash)})

if __name__ == '__main__':
    app.run(debug=True)
