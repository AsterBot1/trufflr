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
