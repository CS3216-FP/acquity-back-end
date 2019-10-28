#!/usr/bin/env bash
poetry run black .
poetry run isort -y
poetry export --without-hashes -f requirements.txt > requirements.txt
