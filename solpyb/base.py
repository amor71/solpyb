import base64
import inspect
import os
import struct
from typing import List, Optional

from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.core import RPCException
from solana.system_program import (CreateAccountWithSeedParams,
                                   create_account_with_seed)
from solana.transaction import AccountMeta, Transaction, TransactionInstruction

from solpyb.connectivity import connect, retry

debug_enabled = bool(int(os.getenv("SOLPYB_DEBUG_ENABLED", 0)))
solana_network: str = os.getenv(
    "SOLPYB_NETWORK", "https://api.devnet.solana.com"
)


class SolBase:
    sizing = {type(float()): 4, type(int()): 4}
    unpack_type = {type(float()): "f", type(int()): "i"}
    seed = "solpyb3"

    def __init__(self, program_id: str, payer: Keypair):
        self.program_id = program_id
        self.program_key = PublicKey(self.program_id)

        self.payer = payer
        self.client: Optional[AsyncClient] = None
        self.response_key: Optional[PublicKey] = None

        if debug_enabled:
            print(f"loaded payer {payer}")

    def _calc_response_size(self) -> int:
        return sum(
            self.sizing[prop_type]
            for _, prop_type in inspect.get_annotations(self).items()
        )

    async def _connect(self):
        if not self.client:
            self.client = await connect(solana_network)
            if debug_enabled:
                print(f"Connected to {solana_network}")

    async def _set_response_account(self):
        await self._connect()

        response_size = self._calc_response_size()
        rent_lamports = (
            await retry(
                self.client.get_minimum_balance_for_rent_exemption,
                response_size,
            )
        )["result"]

        if debug_enabled:
            print(f"program size {response_size} rent:{rent_lamports}")

        self.response_key = PublicKey.create_with_seed(
            self.payer.public_key, self.seed, self.program_key
        )

        instruction = create_account_with_seed(
            CreateAccountWithSeedParams(
                from_pubkey=self.payer.public_key,
                new_account_pubkey=self.response_key,
                base_pubkey=self.payer.public_key,
                seed=self.seed,
                lamports=rent_lamports,
                space=response_size,
                program_id=self.program_key,
            )
        )
        trans = Transaction().add(instruction)
        try:
            trans_result = await retry(
                self.client.send_transaction, trans, self.payer
            )
            await retry(
                self.client.confirm_transaction,
                trans_result["result"],
                "finalized",
                5.0,
            )

            if debug_enabled:
                print(f"Created account {self.response_key}")

        except RPCException:
            if debug_enabled:
                print(f"Reusing account {self.response_key}")

    def to_bytes(self, *args) -> bytes:
        """How to pack values to bytes. May be overwritten.

        The default encoding behavior is to treat *args as a list of floats.
        The list is encoded with the fulling rules:
        1. If the list has values < 256 (.e.g could be encoded as a single byte)
           prefix the list with 0 in the first byte,
        2. Otherwise prefix the list with 1 in the first byte, meaning each float
           will be encoded in two bytes.

        The fractional part is encoded in a single byte rounded to two decimal points.
        Example 1: [10.6, 8.85, 15.678] -> [0 10 6 8 85 15 68]
        Example 2: [500.123, 878.5, 10.0] -> [1 1 244 12 3 110 5 0 10 0]

        Input:
            args : assumed to be list of float, overwrite for different implementation.
        """
        raw_data = [
            (int(x), int(str(round(x, 2)).split(".")[1])) for x in args[0]
        ]
        whole, _ = zip(*raw_data)
        bytes_data: List = []
        if max(whole) >= 256:
            for tup in raw_data:
                bytes_data.append(tup[0] // 256)
                bytes_data.append(tup[0] % 256)
                bytes_data.append(tup[1])
            return bytes([1] + bytes_data)
        else:
            for tup in raw_data:
                bytes_data.append(tup[0])
                bytes_data.append(tup[1])

            return bytes([0] + bytes_data)

    async def _parse_response(self):
        base64_result = (
            await retry(self.client.get_account_info, self.response_key)
        )["result"]["value"]["data"]

        unpack_format: str = "".join(
            [
                self.unpack_type[prop_type]
                for _, prop_type in inspect.get_annotations(self).items()
            ]
        )
        if debug_enabled:
            print(f"unpacking format:{unpack_format}")
        vals = struct.unpack(unpack_format, base64.b64decode(base64_result[0]))
        if debug_enabled:
            print(f"unpacked {vals}")
        for i, property_name in enumerate(
            inspect.get_annotations(self).keys()
        ):
            setattr(self, property_name, vals[i])
            if debug_enabled:
                print(f"added {property_name}={vals[i]}")

    async def __call__(self, *args):
        await self._set_response_account()

        payload_to_contract: bytes = self.to_bytes(*args)

        if debug_enabled:
            print(f"Prepared payload of {len(payload_to_contract)} bytes")
        instruction = TransactionInstruction(
            keys=[
                AccountMeta(
                    pubkey=self.response_key,
                    is_signer=False,
                    is_writable=True,
                ),
            ],
            program_id=self.program_key,
            data=payload_to_contract,
        )
        recent_blockhash = (await retry(self.client.get_recent_blockhash))[
            "result"
        ]["value"]["blockhash"]
        trans = Transaction(
            recent_blockhash=recent_blockhash, fee_payer=self.payer.public_key
        ).add(instruction)

        try:
            trans_result = await retry(
                self.client.send_transaction, trans, self.payer
            )
        except RPCException as e:
            print(
                f"SOLANA ERROR {e} for payload of {len(payload_to_contract)} bytes"
            )
            return None

        await retry(
            self.client.confirm_transaction,
            trans_result["result"],
            "finalized",
            5.0,
        )

        await self._parse_response()

        return True
