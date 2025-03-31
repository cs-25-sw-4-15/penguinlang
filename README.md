# penguin GB lang

## Setup

1. install the UV package installer

Jeg gider ikke dette uv noget længere. tror vi flytter det til miniconda

With PyPI:
```bash
pip install uv
```
2. Create UV virtual environment
``` bash
uv venv --python 3.11
```
3. Enter venv

Unix:
```bash
source .venv/bin/activate
```
Win:
```powershell
.venv\Scripts\activate
```
3. Install Python requirements
```bash
uv pip install -r pyproject.toml
```
4. Generate ANTLR4 lexer/parser files
```bash
antlr4 -Dlanguage=Python3 -o generated/ grammar/penguin.g4
```
4. Fetch RGBDS
```

```

- Exit virtual environment
```bash
deactivate
```

## Running
```bash
uv run SCRIPTPATH.FILEEXTENTION
```

## Building


## Testing


## CI
