import json
import os
from typing import Optional

from solana.keypair import Keypair


def load_wallet(wallet_filename: Optional[str] = None) -> Keypair:
    """Loads wallet key-pair from file. If not parameter is present assuming default
    location (~/.config/solana/id.json)"""

    if not wallet_filename:
        home_directory = os.path.expanduser("~")
        wallet_filename = f"{home_directory}/.config/solana/id.json"

    with open(wallet_filename) as f:
        data = json.load(f)

        return Keypair.from_secret_key(bytes(data))
