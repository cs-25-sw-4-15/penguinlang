# penguin GB lang

## Pre

Installer 



## Setup

win: py, linux: python3, mac: something

0. Installer Python 3.10 or higher
1. Upgade pip
```bash
python3 -m pip install --upgrade pip
```
2. Lav python enviroment
```bash
python3 -m venv .venv
```
3. Aktiver enviroment
  - Windows
```bash
.\.venv\Scripts\activate
```
  - macOS/Linux/wsl
```bash
source .venv/bin/activate
```
4. Install Python requirements
```bash
python3 -m pip install -r .\requirements.txt
```
5. Install RGBDS
```bash
mkdir src/rgbds
wget -O src/rgbds/rgbds-0.9.1-linux-x86_64.tar.xz https://github.com/gbdev/rgbds/releases/download/v0.9.1/rgbds-0.9.1-linux-x86_64.tar.xz
tar xf src/rgbds/rgbds-0.9.1-linux-x86_64.tar.xz -C src/rgbds
rm src/rgbds/rgbds-0.9.1-linux-x86_64.tar.xz
```
6. Generate ANTLR4 lexer/parser files
```bash
antlr4 -Dlanguage=Python3 -visitor -o src/generated/ src/grammar/penguin.g4
```


- Exit virtual environment
```bash
deactivate
```

## Testing
```bash
pytest
```

## Syntax opitionation
```bash
flake8 \[optional dir or file\]
```
Error codes: https://pycodestyle.pycqa.org/en/latest/intro.html#error-codes

## CLI
```bash
py cli.py COMMAND [option] ...
```

