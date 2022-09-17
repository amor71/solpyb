#!/bin/bash

export CODECOV_TOKEN=260f22ca-4d24-408f-8d18-b67c1f294c41

echo "Generate Coverage Report"
python3 -m pytest -s --cov --cov-report xml

echo "upload coverage report"
codecov -vt $CODECOV_TOKEN