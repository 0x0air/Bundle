from web3 import Web3
from solcx import compile_source, install_solc
import logging

# ========== Basic Configuration ==========
RPC_URL = "" #
PRIVATE_KEY = ""  # ⚠️ Your private key
SOLC_VERSION = "0.8.20"

# ========== Logging Configuration ==========
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ========== Initialize Web3 ==========
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise ConnectionError("❌ RPC connection failed, please check if RPC_URL is correct")

account = w3.eth.account.from_key(PRIVATE_KEY)
address = account.address
logger.info(f"🔗 Connected to network | Account: {address}")

# ========== Compile Contract ==========
install_solc(SOLC_VERSION)

contract_source = '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BatchSender {
    function distribute(address[] calldata recipients, uint256[] calldata amounts) external payable {
        require(recipients.length == amounts.length, "Mismatched arrays");
        uint256 total = 0;
        for (uint256 i = 0; i < amounts.length; i++) {
            total += amounts[i];
        }
        require(msg.value >= total, "Insufficient ETH sent");
        for (uint256 i = 0; i < recipients.length; i++) {
            payable(recipients[i]).transfer(amounts[i]);
        }
    }
}
'''

compiled = compile_source(contract_source, output_values=["abi", "bin"], solc_version=SOLC_VERSION)
_, interface = compiled.popitem()
abi = interface["abi"]
bytecode = interface["bin"]
logger.info("✅ Contract compiled successfully")

# ========== Get Gas Info (Automatic) ==========
gas_price = w3.eth.gas_price  # Automatically fetch gas price from RPC
logger.info(f"⛽ Current gasPrice: {w3.from_wei(gas_price, 'gwei')} gwei")

# ========== Build Deployment Transaction ==========
BatchSender = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(address)

tx = BatchSender.constructor().build_transaction({
    "chainId": w3.eth.chain_id,
    "from": address,
    "nonce": nonce,
    "gasPrice": gas_price,  # Auto gas price
})

# Estimate gasLimit (automatic)
gas_estimate = w3.eth.estimate_gas(tx)
tx["gas"] = gas_estimate
logger.info(f"📏 Estimated gasLimit: {gas_estimate}")

# ========== Sign and Send Transaction ==========
signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
logger.info(f"🚀 Deployment transaction sent | Hash: {tx_hash.hex()}")

# ========== Wait for Deployment Confirmation ==========
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
if receipt.status == 1:
    logger.info(f"🎉 Deployment successful! Contract address: {receipt.contractAddress}")
else:
    logger.error("❌ Deployment failed!")
