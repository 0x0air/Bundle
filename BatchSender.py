"""
Batch ETH Transfer Script
=========================

This script automates batch ETH transfers using a deployed smart contract
that supports a `distribute(address[], uint256[]) payable` function.

Features:
- Reads recipient addresses and amounts from a text file (`receiver_addresses.txt`)
- Supports default transfer amount when not specified
- Automatically derives sender address from a private key
- Dynamically fetches gas price and estimates gas limit
- Signs and broadcasts the transaction to the blockchain

Author: 0x0air
License: MIT
"""

from web3 import Web3
from eth_account import Account

# === Configuration === 
RPC_URL = "" # ⚠️ RPC endpoint of the blockchain network (e.g. Infura, Alchemy, or local node)
PRIVATE_KEY = ""  # ⚠️ Your private key (without 0x prefix)
DEFAULT_AMOUNT_ETH = 0.00001  # ⚠️ Default transfer amount (in ETH)

# === Derive wallet address ===
account = Account.from_key(PRIVATE_KEY)
SENDER_ADDRESS = account.address

# === Contract info ===
CONTRACT_ADDRESS = ""  # ⚠️ Replace with deployed contract address
contract_abi = [
    {
        "inputs": [
            {"internalType": "address[]", "name": "recipients", "type": "address[]"},
            {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"},
        ],
        "name": "distribute",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    }
]

# === Read recipients and amounts from file ===
recipients = []
amounts_eth = []

with open("receiver_addresses.txt", "r") as file:
    for line in file:
        line = line.strip()
        if not line or line.startswith("#"):
            continue  # Skip empty lines and comments
        if "---" in line:
            addr, amount = line.split("---")
            recipients.append(Web3.to_checksum_address(addr.strip()))
            amounts_eth.append(float(amount.strip()))
        else:
            recipients.append(Web3.to_checksum_address(line.strip()))
            amounts_eth.append(DEFAULT_AMOUNT_ETH)

# === Convert amounts to wei ===
amounts_wei = [Web3.to_wei(a, "ether") for a in amounts_eth]
total_value = sum(amounts_wei)

# === Initialize Web3 and contract ===
w3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=contract_abi
)

# === Dynamic gas configuration ===
nonce = w3.eth.get_transaction_count(SENDER_ADDRESS)
gas_price = w3.eth.gas_price  # Get current gas price

# Estimate gas limit (with safety buffer)
estimated_gas = contract.functions.distribute(
    recipients, amounts_wei
).estimate_gas({"from": SENDER_ADDRESS, "value": total_value})
gas_limit = int(estimated_gas * 1.2)  # +20% buffer to reduce risk of out-of-gas

# === Build transaction ===
txn = contract.functions.distribute(recipients, amounts_wei).build_transaction({
    "from": SENDER_ADDRESS,
    "value": total_value,
    "nonce": nonce,
    "gas": gas_limit,
    "gasPrice": gas_price,
    "chainId": w3.eth.chain_id,
})

# === Sign and send transaction ===
signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

print(f"🚀 Transaction sent! Tx Hash: {tx_hash.hex()}")
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("✅ Transaction confirmed.")
