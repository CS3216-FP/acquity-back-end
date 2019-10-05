# Acquity: Back-End

## Setup
- install pip3
```
sudo apt install python3-pip
```
- install Poetry (https://poetry.eustace.io), prerelease version
```
curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | env POETRY_PREVIEW=1 python
```
- install dependencies
```
poetry install
```

## Run app
```
./launch.sh
```

## Lint
Auto-fix: `./lint_fix.sh`

Check (is run in CI): `./lint.sh`
