from solpyb import load_wallet


def test_load_default_wallet():
    default_wallet = load_wallet()

    print(default_wallet)

    return True
