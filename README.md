[![Upload Python Package](https://github.com/amor71/solpyb/actions/workflows/python-publish.yml/badge.svg)](https://github.com/amor71/solpyb/actions/workflows/python-publish.yml)
[![codecov](https://codecov.io/gh/amor71/solpyb/branch/master/graph/badge.svg?token=gUJ78Gdh6q)](https://codecov.io/gh/amor71/solpyb)

# solpyb

Pythonic Bridge to Solana Programs.

## Overview

The project simplifies executing and getting responses from Solana Programs (a.k.a *Smart Contracts*), that are running on the Solana [Blockchain](https://solana.com/).

## Setup

`pip install solpyb`

## A Simple Example

```python
    import asyncio
    from solpyb import SolBase, load_wallet


    class MyProgram(SolBase):
        slope: float
        intercept: float


    contract = MyProgram(
        program_id="64ZdvpvU73ig1NVd36xNGqpy5JyAN2kCnVoF7M4wJ53e", payer=load_wallet()
    )
    if asyncio.run(contract([10.5, 20.7, 30.8, 40.12, 50.20, 60.0])):
        print(f"slope: {contract.slope} intercept {contract.intercept}")
```

*(This script is complete, it should run "as is")*

What's going on here:

* "64ZdvpvU73ig1NVd36xNGqpy5JyAN2kCnVoF7M4wJ53e" is a Solana Program (a.k.a *Smart Contract*) that performs a [Linear regression](https://en.wikipedia.org/wiki/Linear_regression) on set of points and returns the slope and intercept as floats.
* load_wallet() loads the default wallet keys (`.config/solana/id.json`), as the payer for the transaction.
* *MyProgram* class implement a Pythonic wrapper class. Calling the call creates a transaction on chain and result is returned,
* *SolBase* populates `slope` and `intercept` with the values returned from the Blockchain.
