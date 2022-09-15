from solpyb import SolBase


class MyProgram(SolBase):
    slope: float
    intercept: float


def test_basic_flow():
    contract = MyProgram("64ZdvpvU73ig1NVd36xNGqpy5JyAN2kCnVoF7M4wJ53e")
    if contract([10, 5, 20, 7, 30, 8, 40, 12, 50, 20, 60, 15]):
        print(f"slope: {contract.slope} intercept {contract.intercept}")
        return True
    else:
        raise AssertionError("Expected True.")
