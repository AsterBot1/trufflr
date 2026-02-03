#!/usr/bin/env python3
"""
Trufflr guider 91: deploy and call the Trufflr contract (lane anchor / guider seal).
Uses web3.py; compile with Hardhat first. Set RPC_URL and DEPLOYER_PRIVATE_KEY to deploy.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from web3 import Web3
except ImportError:
    print("Install dependencies: pip install -r requirements.txt")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARTIFACT_PATH = PROJECT_ROOT / "artifacts" / "contracts" / "Trufflr.sol" / "Trufflr.json"


def compile_contract():
    if ARTIFACT_PATH.exists():
        return True
    print("Compiling (npx hardhat compile)...")
    r = subprocess.run(
        ["npx", "hardhat", "compile"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print(r.stderr or r.stdout)
        return False
    return ARTIFACT_PATH.exists()


def load_artifact():
    with open(ARTIFACT_PATH, encoding="utf-8") as f:
        return json.load(f)


def deploy(w3, account):
    artifact = load_artifact()
    contract = w3.eth.contract(abi=artifact["abi"], bytecode=artifact["bytecode"])
    tx = contract.constructor().build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
    })
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt["status"] != 1:
        raise RuntimeError("Deploy tx failed")
    return receipt["contractAddress"]


def main():
    rpc_url = os.environ.get("RPC_URL", "http://127.0.0.1:8545")
    pk = os.environ.get("DEPLOYER_PRIVATE_KEY", "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
    deployed_address = os.environ.get("TRUFFLR_ADDRESS")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"Cannot connect to RPC: {rpc_url}")
        sys.exit(1)
    print(f"Connected (chain_id={w3.eth.chain_id})")

    if not compile_contract():
        print("Compilation failed.")
        sys.exit(1)

    artifact = load_artifact()
    abi = artifact["abi"]

    if deployed_address:
