from solpyb import load_wallet


def test_load_default_wallet():
    default_wallet = load_wallet()

    print(default_wallet)

    return True


def test_load_wrong_wallet():
    try:
        load_wallet("_this_file_will_never_exist_")
    except OSError:
        return True

    raise AssertionError("Expected to fail")
