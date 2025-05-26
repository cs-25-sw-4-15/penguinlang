# penguin GB lang

## Setup
0. Installer Python 3.10 or higher
1. Upgade pip
```bash
python3 -m pip install --upgrade pip
```
2. Create python enviroment
```bash
python3 -m venv .venv
```
3. Aktiver enviroment
```bash
source .venv/bin/activate
```
4. Install Python requirements
```bash
python3 -m pip install -r requirements.txt
```
5. Install RGBDS
```bash
mkdir -p ./src/rgbds
wget -O ./src/rgbds/rgbds-0.9.1-linux-x86_64.tar.xz https://github.com/gbdev/rgbds/releases/download/v0.9.1/rgbds-0.9.1-linux-x86_64.tar.xz
tar xf ./src/rgbds/rgbds-0.9.1-linux-x86_64.tar.xz -C ./src/rgbds
```
6. Generate ANTLR4 lexer/parser files

With python:
```bash
antlr4 -Dlanguage=Python3 -visitor -o src/generated/ src/grammar/penguin.g4
```
Or with java:
```bash
sudo apt-get install -y default-jre
curl -o antlr-4.13.2-complete.jar https://www.antlr.org/download/antlr-4.13.2-complete.jar
java -Xmx500M -cp ./antlr-4.13.2-complete.jar org.antlr.v4.Tool -Dlanguage=Python3 -visitor -o src/generated -Xexact-output-dir src/grammar/penguin.g4
ls -R src/generated
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
flake8 $?
```
Error codes: https://pycodestyle.pycqa.org/en/latest/intro.html#error-codes

## CLI
```bash
py cli.py COMMAND [option] ...
```

Commands:
- `cst` - options: penguin soruce code filepath
- `ast` - options: penguin soruce code filepath
- `taast` - options: penguin soruce code filepath
- `compile` - options: penguin soruce code filepath
