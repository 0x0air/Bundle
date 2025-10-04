# 📦 Batch Gas_Token Transfer Contract and Script Usage Guide

## I. 🧾 Function Overview

This tool consists of a Solidity smart contract and a Python script.
When used together, it enables batch ETH transfers to multiple addresses.
It supports assigning custom amounts to certain addresses, while others use a default amount.

✅ Automatically recognizes custom and default amounts

✅ Dynamically fetches gasPrice and gasLimit

✅ Uses receiver_addresses.txt to configure transfer targets

✅ Automatically calculates the total transfer amount (msg.value)

✅ One-click batch transaction execution


## II. 📌 Script execution order

#### 1. Deploy contracts
• Run Deploy_contracts.py to deploy BatchSender_contract.sol.

• Alternatively, you can deploy the contract using [Remix IDE](https://remix.ethereum.org/), but make sure to deploy it on the same blockchain network where you want to use BatchSender.

• After deployment, copy the contract address returned by the script.

#### 2. Configure BatchSender.py
• Open BatchSender.py and fill in the following:

• RPC_URL → Your RPC endpoint

• PRIVATE_KEY → Your private key

• CONTRACT_ADDRESS → Paste the deployed contract address

DEFAULT_AMOUNT_ETH → Default ETH amount to send (if not specified per address)

#### 3. Prepare Recipient Addresses

• Edit receiver_addresses.txt to list all recipient addresses and amounts.

• Supported formats per line:
```
<address>---<amount>   # Custom ETH amount
<address>              # Uses default amount set in BatchSender.py
```

#### 4. Execute Batch Sending

• Run BatchSender.py.

• The script will read the addresses and amounts from receiver_addresses.txt and send ETH in a single batch transaction.


## II. 📜 Contract Description (BatchSender.sol)

Contract Name: BatchSender
Core Function:
```
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title BatchSender
/// @notice A simple contract to send ETH to multiple recipients in a single transaction
/// @dev Uses `transfer()` for safety against reentrancy
contract BatchSender {

    /// @notice Sends ETH to multiple recipients
    /// @param recipients Array of addresses to receive ETH
    /// @param amounts Array of amounts (in wei) corresponding to each recipient
    /// @dev The lengths of recipients and amounts must match. msg.value must cover total sum.
    function distribute(address[] calldata recipients, uint256[] calldata amounts) external payable {
        // Ensure recipients and amounts arrays have the same length
        require(recipients.length == amounts.length, "Mismatched arrays");

        // Calculate total ETH required for all transfers
        uint256 total = 0;
        for (uint256 i = 0; i < amounts.length; i++) {
            total += amounts[i];
        }

        // Ensure the sender sent enough ETH to cover all transfers
        require(msg.value >= total, "Insufficient ETH sent");

        // Send ETH to each recipient
        for (uint256 i = 0; i < recipients.length; i++) {
            // `transfer` forwards 2300 gas and reverts on failure
            payable(recipients[i]).transfer(amounts[i]);
        }
    }
}
```
Accepts two arrays, recipients and amounts, where addresses and amounts correspond one-to-one.
msg.value must be greater than or equal to the total sum of all transfer amounts.
The contract sends ETH to each specified address in batch.


## IV. 📄 receiver_addresses.txt Format

Supports two formats, configured line by line:

```
<address>---<amount>     # Specify a custom amount (in ETH)
<address>                # Use the default amount (defined in the script)
```


Example:

0x1A98B82b7b14a9C3987d87555C7a8F4D224293xxx---0.001

0x910A555fCFb03C92573C857b14EBbB40e773axxx---0.0001

0xff5c91ec5b6e66b1a63f490200dbaa362562axxx


Finally, simply run the script to start the batch transfer.
