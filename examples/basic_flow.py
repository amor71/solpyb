import asyncio

from solpyb import SolBase, load_wallet


class MyProgram(SolBase):
    slope: float
    intercept: float


contract = MyProgram(
    program_id="64ZdvpvU73ig1NVd36xNGqpy5JyAN2kCnVoF7M4wJ53e",
    payer=load_wallet(),
)
if asyncio.run(contract([10.5, 20.7, 30.8, 40.12, 50.20, 60.0])):
    print(f"slope: {contract.slope} intercept {contract.intercept}")
