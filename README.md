# CodeDigest

**CodeDigest** is a lightweight Python CLI tool that aggregates an entire code repository into a **single AI‑friendly file (XML, JSON, or YAML)**. 

It preserves structure, embeds readable source code (wrapped in CDATA for XML), and references other assets.

This tool is ideal for **AI ingestion**, **project snapshots**, **documentation**, or **audit purposes**.

## Features

- Recursive folder walk — scans all files and directories
- Directory structure recap block
- File‑type summary and directory tree (optional)  
- File type statistics (e.g. number of scripts, images, binaries) (optional)  
- AI-optimized output: text files embedded, others tagged
- Single output file in `.xml`, `.json`, or `.yaml` format
- Embeds text files (via CDATA in XML) 
- Auto‑selects output format based on extension  
- Flexible CLI filters: include/exclude by extension or type
- CLI-friendly, only one dependency (`PyYAML` for YAML)
- MIT licensed & lightweight

### Academic Publication Support

This project is also ideal for academic publications in **LaTeX**: it can aggregate all split files (e.g., per‑chapter or per‑section exports) into a single consolidated digest.

## Screenshot

![CodeDigest usage](assets/screenshot.png)
_Example: Output digest shown in CLI (Local "Demo" repository exported to a single XML file)_

## Installation

### Option 1 – Install via `pip`

> You can build and install the CLI tool using `pip`, which relies on the local `pyproject.toml` configuration:
```
pip install .
```

### Option 2 – Run without installing

> You can also run CodeDigest directly without installing anything globally:
```
python3 codedigest.py --path ./myrepo --output digest.xml --timestamp
```

## Dependencies

This script uses only Python's standard library, **except** for:

- [`PyYAML`](https://pypi.org/project/PyYAML/) – required for `.yaml` or `.yml` export formats.

### Dependencies Installation

```
pip install PyYAML
```

## Usage

```
python3 codedigest.py --path /my/repo --output digest.xml
python3 codedigest.py --path /my/repo --output digest.yaml
python3 codedigest.py --path /my/repo --output digest.json
```
    
### Options

| Option             | Description |
|--------------------|-------------|
| --timestamp        | Timestamp insertion in output filename |
| --skip-other       | Skip files of type "other" (unknown/binary) |
| --only-text        | Include only source/text files |
| --include-ext      | Only include files with these extensions (e.g. `.py .md`) |
| --exclude-dir      | Ignore specific folders (e.g. `.git`, `__pycache__`) |
| --no-summary       | Skip the file-type count block |
| --no-structure     | Skip directory tree listing |
| --version          | Show current version (`0.1`) |


## Advanced Usage Examples

### Only include specific extensions for a code Project (`.py`, `.yaml`, `.ini`)
```
python3 codedigest.py --path ./myrepo --output digest.xml --include-ext .py .yaml .ini
```

### Only include specific extensions for an Academic Publication (`.tex`, `.bib`)
```
python3 codedigest.py --path ./latex_paper --output digest.json --include-ext .tex .bib
```

### Exclude binary or unknown file types
```
python3 codedigest.py --path ./myrepo --output digest.yaml --skip-other
```

### Include only text files (no reference to images, binaries, etc.)
```
python3 codedigest.py --path ./myrepo --output digest.json --only-text
```

### Override default excluded directories
```
python3 codedigest.py --path ./myrepo --output digest.yaml --exclude-dir .venv build dist node_modules
```

### Skip directory tree and file-type summary
```
python3 codedigest.py --path ./myrepo --output digest.xml --no-summary --no-structure
```

### Full power usage with all controls
```
python3 codedigest.py --path ./myrepo \
  --timestamp \
  --output digest.xml \
  --include-ext .py .md .sh \
  --exclude-dir .git temp node_modules \
  --skip-other \
  --only-text \
  --no-summary
```


## Version

This is version `v0.1`.


## License

**MIT** — free to use, modify, and distribute.


## Author

Created by [@TristanInSec](https://github.com/TristanInSec)
