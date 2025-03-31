# penguin GB lang

## Pre

Installer 



## Setup

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
python -m pip install -r .\requirements.txt
```
5. Install RGBDS
```

```
6. Generate ANTLR4 lexer/parser files
```bash
antlr4 -Dlanguage=Python3 -o src/generated/ src/grammar/penguin.g4
```


- Exit virtual environment
```bash
deactivate
```

## Running
```bash
py SCRIPTPATH.FILEEXTENTION INPUTFILE -o OUTPUTFILE
```

o: optional

## Testing
```bash
pytest tests/tester.py
```
```bash
pytest -q tests/tester.py
```

## CI
