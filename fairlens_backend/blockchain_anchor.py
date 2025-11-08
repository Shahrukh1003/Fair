"""
Blockchain Anchor Module for FairLens

Purpose: Simulate anchoring fairness audit hashes to a public blockchain
for tamper-proof, publicly verifiable compliance evidence.

This is a demonstration of how fairness logs can be made immutable and
transparent using blockchain technology. In production, this would connect
to a real blockchain network like Polygon, Ethereum, or Hyperledger.

How it fits: This is the TRANSPARENCY layer in the FairLens pipeline.
Data → Metric → Alert → Log → [Blockchain Anchor] → Public Verification
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional


ANCHOR_LOG_FILE = os.path.join(os.path.dirname(__file__), 'blockchain_anchors.jsonl')


def generate_mock_tx_id(record_hash: str) -> str:
    """
    Generate a mock blockchain transaction ID.
    
    In production, this would be a real transaction hash from submitting
    the record hash to a blockchain network.
    
    Parameters:
    -----------
    record_hash : str
        The SHA256 hash of the fairness record
    
    Returns:
    --------
    str : Mock transaction ID in blockchain format (0x...)
    """
    # Create a deterministic but unique-looking transaction ID
    combined = f"fairlens_anchor_{record_hash}_{datetime.utcnow().isoformat()}"
    tx_hash = hashlib.sha256(combined.encode()).hexdigest()
    return f"0x{tx_hash[:64]}"


def anchor_to_blockchain(
    record_hash: str,
    model_name: str = "loan_approval_v1",
    metadata: Dict = None
) -> Dict:
    """
    Anchor a fairness record hash to the blockchain (simulated).
    
    In production, this function would:
    1. Connect to blockchain network (e.g., Polygon testnet)
    2. Create a transaction with the hash in the data field
    3. Submit transaction and wait for confirmation
    4. Return the transaction ID and block number
    
    For this demo, we simulate the process and store anchors locally.
    
    Parameters:
    -----------
    record_hash : str
        SHA256 hash of the fairness record to anchor
    model_name : str
        Name of the AI model being monitored
    metadata : Dict, optional
        Additional metadata to store with the anchor
    
    Returns:
    --------
    Dict containing:
        - tx_id: blockchain transaction ID
        - block_number: block where transaction was included (simulated)
        - timestamp: when anchor was created
        - record_hash: the hash that was anchored
        - network: blockchain network name
        - explorer_url: URL to view transaction (simulated)
    """
    # Generate mock transaction ID
    tx_id = generate_mock_tx_id(record_hash)
    
    # Simulate block number (incrementing)
    block_number = _get_next_block_number()
    
    # Create anchor record
    anchor = {
        "tx_id": tx_id,
        "block_number": block_number,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "record_hash": record_hash,
        "model_name": model_name,
        "network": "polygon-mumbai-testnet",  # Simulated testnet
        "explorer_url": f"https://mumbai.polygonscan.com/tx/{tx_id}",
        "metadata": metadata or {},
        "status": "confirmed"
    }
    
    # Store anchor in local log
    _save_anchor(anchor)
    
    return anchor


def get_anchor(record_hash: str) -> Optional[Dict]:
    """
    Retrieve blockchain anchor information for a specific record hash.
    
    Parameters:
    -----------
    record_hash : str
        The SHA256 hash to look up
    
    Returns:
    --------
    Dict or None : Anchor information if found, None otherwise
    """
    if not os.path.exists(ANCHOR_LOG_FILE):
        return None
    
    try:
        with open(ANCHOR_LOG_FILE, 'r') as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        anchor = json.loads(line)
                        if anchor.get('record_hash') == record_hash:
                            return anchor
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass
    
    return None


def get_recent_anchors(limit: int = 10) -> List[Dict]:
    """
    Get the most recent blockchain anchors.
    
    Parameters:
    -----------
    limit : int
        Number of recent anchors to retrieve
    
    Returns:
    --------
    List[Dict] : List of anchor records
    """
    if not os.path.exists(ANCHOR_LOG_FILE):
        return []
    
    try:
        with open(ANCHOR_LOG_FILE, 'r') as fh:
            lines = fh.readlines()
        
        recent_lines = lines[-limit:] if len(lines) > limit else lines
        
        anchors = []
        for line in recent_lines:
            line = line.strip()
            if line:
                try:
                    anchors.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return anchors
    except Exception:
        return []


def verify_anchor(record_hash: str, tx_id: str) -> Dict:
    """
    Verify that a record hash was anchored with a specific transaction ID.
    
    In production, this would query the blockchain to confirm the
    transaction exists and contains the correct hash.
    
    Parameters:
    -----------
    record_hash : str
        The hash to verify
    tx_id : str
        The transaction ID to check
    
    Returns:
    --------
    Dict containing:
        - verified: True if anchor is valid
        - message: verification result message
        - anchor: the anchor data if found
    """
    anchor = get_anchor(record_hash)
    
    if not anchor:
        return {
            "verified": False,
            "message": "No blockchain anchor found for this record hash",
            "record_hash": record_hash
        }
    
    if anchor['tx_id'] != tx_id:
        return {
            "verified": False,
            "message": "Transaction ID mismatch",
            "expected": anchor['tx_id'],
            "provided": tx_id
        }
    
    return {
        "verified": True,
        "message": "Blockchain anchor verified successfully",
        "anchor": anchor
    }


def _save_anchor(anchor: Dict) -> None:
    """
    Save anchor to local JSONL file.
    
    Parameters:
    -----------
    anchor : Dict
        The anchor data to save
    """
    os.makedirs(os.path.dirname(ANCHOR_LOG_FILE), exist_ok=True)
    
    with open(ANCHOR_LOG_FILE, 'a') as fh:
        json.dump(anchor, fh)
        fh.write('\n')
        fh.flush()


def _get_next_block_number() -> int:
    """
    Get the next simulated block number.
    
    Returns:
    --------
    int : Next block number (increments with each anchor)
    """
    anchors = get_recent_anchors(limit=1)
    if anchors:
        return anchors[-1].get('block_number', 1000000) + 1
    return 1000000  # Starting block number


"""
WHY BLOCKCHAIN ANCHORING MATTERS:

1. PUBLIC VERIFIABILITY:
   - Anyone can verify fairness records haven't been tampered with
   - No need to trust the company - trust the blockchain
   - Transparent compliance for regulators and public

2. IMMUTABILITY:
   - Once anchored, records cannot be altered or deleted
   - Provides strongest possible audit trail
   - Meets highest compliance standards

3. NON-REPUDIATION:
   - Company cannot deny past fairness results
   - Timestamped proof of when fairness was checked
   - Legal evidence in discrimination cases

REAL-WORLD USE CASES:

Banking:
- Anchor daily fairness reports to blockchain
- Regulators can verify compliance independently
- Public can audit fairness claims

Healthcare:
- Prove diagnostic AI fairness over time
- Transparent bias monitoring for medical devices
- Patient advocacy groups can verify claims

Government:
- Transparent welfare eligibility scoring
- Public verification of fair AI use
- Accountability for automated decisions

HOW IT WORKS (Production Implementation):

1. HASH GENERATION:
   - Compute SHA256 of fairness record
   - Hash contains: DIR, rates, timestamp, model ID

2. BLOCKCHAIN SUBMISSION:
   - Connect to blockchain network (Polygon, Ethereum)
   - Create transaction with hash in data field
   - Pay small gas fee (< $0.01 on Polygon)
   - Wait for transaction confirmation

3. VERIFICATION:
   - Anyone can query blockchain with transaction ID
   - Blockchain returns the anchored hash
   - Compare with local record hash
   - If match → record is authentic

COST ANALYSIS:

Polygon (Recommended):
- Transaction cost: ~$0.001 per anchor
- Confirmation time: ~2 seconds
- Scalability: 7,000+ TPS

Ethereum:
- Transaction cost: ~$1-5 per anchor
- Confirmation time: ~15 seconds
- More established but expensive

Hyperledger (Private):
- No transaction costs
- Instant confirmation
- Requires permission to access

IMPLEMENTATION STEPS FOR PRODUCTION:

1. Install web3.py library:
   pip install web3

2. Get blockchain node access:
   - Infura (https://infura.io)
   - Alchemy (https://alchemy.com)
   - Or run your own node

3. Create wallet for transactions:
   - Generate private key
   - Fund with small amount of MATIC/ETH
   - Store key securely (AWS KMS, HashiCorp Vault)

4. Modify anchor_to_blockchain():
   from web3 import Web3
   
   w3 = Web3(Web3.HTTPProvider('https://polygon-mumbai.infura.io/v3/YOUR_KEY'))
   
   tx = {
       'to': '0x0000000000000000000000000000000000000000',
       'value': 0,
       'gas': 21000,
       'gasPrice': w3.eth.gas_price,
       'nonce': w3.eth.get_transaction_count(wallet_address),
       'data': record_hash.encode()
   }
   
   signed_tx = w3.eth.account.sign_transaction(tx, private_key)
   tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
   
   return tx_hash.hex()

5. Add verification endpoint:
   - Query blockchain for transaction
   - Extract data field
   - Compare with local hash

DEMO SIMULATION:
This module simulates the blockchain anchoring process without
requiring actual blockchain access. It demonstrates the concept
and can be easily upgraded to real blockchain integration.

The simulation:
- Generates realistic transaction IDs
- Tracks block numbers
- Provides explorer URLs
- Stores anchors locally

To upgrade to production:
1. Replace generate_mock_tx_id() with real blockchain submission
2. Update verify_anchor() to query actual blockchain
3. Add error handling for network issues
4. Implement retry logic for failed transactions
"""
