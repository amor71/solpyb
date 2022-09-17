import asyncio

from solana.exceptions import SolanaRpcException
from solana.rpc.async_api import AsyncClient


async def retry(coro, *args):
    result = None
    while not result:
        try:
            return await coro(*args)
        except SolanaRpcException:
            await asyncio.sleep(11)

    return result


async def connect(solana_network: str) -> AsyncClient:
    client = AsyncClient(solana_network)
    while not await client.is_connected():
        await asyncio.sleep(10)
        client = AsyncClient(solana_network)

    return client
