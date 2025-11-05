# YAML Reading Core

Small, dependency‑light helper for loading, working with, and saving YAML. It provides a thin wrapper (`YamlFile`) with convenient dot‑path accessors and utilities like required‑key validation and deep merge.

This module aims for safe defaults using `yaml.safe_load` / `yaml.safe_dump`.

## Overview
- Load YAML from disk or from a string
- Work with data via a friendly API (`get`, `set`, `exists_key`, `merge`, `validate_structure`)
- Save YAML back to disk, creating parent directories as needed
- Designed to compose with other modules (e.g., use Temp Files Manager for ephemeral files)

## Features
- File and string loaders
	- `read_yaml(path)` → returns `YamlFile` or raises `FileNotFoundError` if missing/invalid
	- `read_yaml_str(text)` → returns `YamlFile` or raises `ValueError` on invalid YAML
- Data helpers on `YamlFile`
	- Dot‑path access: `get("a.b.c")`, `set("x.y", 42)`, `exists_key(...)`, `has_value(...)`
	- Validation: `has_required_keys([...])`, `validate_structure([...])`
	- Deep merge: `merge({...})` returns a new `YamlFile`
	- Persistence: `save(path)` writes YAML with `allow_unicode=True` and `sort_keys=False`
- Minimal dependency surface (only `pyyaml`)

## Quickstart

Read from a file and access values with dot‑paths:

```python
from cores.yaml_reading_core import YamlReadingCore

yf = YamlReadingCore.read_yaml("./project/config/example.yaml")
db_host = yf.get("database.host", default="localhost")

# Set and save
yf.set("flags.experimental", True)
yf.save("./project/config/example.out.yaml")
```

Load from a YAML string:

```python
from cores.yaml_reading_core import YamlReadingCore

yf = YamlReadingCore.read_yaml_str("""
app:
	name: demo
	version: 1.0
""")

assert yf.exists_key("app.name")
```

Deep‑merge overrides and validate required keys:

```python
from cores.yaml_reading_core import YamlReadingCore

base = YamlReadingCore.read_yaml_str("""
service:
	url: https://api.example.com
	retries: 2
""")

merged = base.merge({"service": {"retries": 5, "timeout": 10}})

required = ["service.url", "service.retries"]
assert merged.validate_structure(required)
```

### With Temp Files Manager
For ephemeral workflows, pair with Temp Files Manager to create a working directory and write intermediate YAML safely:

```python
from managers.temp_files_manager.temp_files_manager import TempFilesManager
from cores.yaml_reading_core import YamlReadingCore

tfm = TempFilesManager()                          # resolves base dir from .config
work_dir = tfm.make_dir(prefix="yaml")

yf = YamlReadingCore.read_yaml_str("name: transient")
yf.save(f"{work_dir}/transient.yaml")

tfm.cleanup(work_dir)                             # remove when done
```

## API

```python
class YamlReadingCore:
		@staticmethod
		def read_yaml(file_path: str | pathlib.Path) -> YamlFile: ...  # raises FileNotFoundError on missing/invalid file

		@staticmethod
		def read_yaml_str(yaml_str: str) -> YamlFile: ...             # raises ValueError on invalid YAML


class YamlFile:
		data: dict
		file_path: pathlib.Path | str | None

		def exists_key(self, key_path: str) -> bool: ...
		def get(self, key_path: str, default: typing.Any | None = None) -> typing.Any: ...
		def set(self, key_path: str, value: typing.Any) -> None: ...

		def has_required_keys(self, required_keys: list[str]) -> bool: ...
		def has_value(self, key_path: str) -> bool: ...
		def validate_structure(self, required_keys: list[str]) -> bool: ...

		def merge(self, override_data: dict) -> "YamlFile": ...      # deep merge; returns new YamlFile
		def to_dict(self) -> dict: ...                                # shallow copy of data
		def save(self, file_path: str | pathlib.Path | None = None) -> bool: ...
```

Notes
- `read_yaml` raises `FileNotFoundError` for missing files or YAML parse errors. Double‑check the path and content.
- `read_yaml_str` raises `ValueError` on invalid YAML.
- `save` returns `True` on success, `False` on failure (e.g., unwritable destination or missing target when no `file_path` was provided at init).
- YAML is written with `allow_unicode=True` and `sort_keys=False` to keep key order stable.

## Requirements & prerequisites
- Python dependency: `pyyaml` (declared in the project `requirements.txt`)

## Troubleshooting
- File load fails with `FileNotFoundError`:
	- Ensure the path exists and is readable. The helper surfaces YAML parse errors as `FileNotFoundError` for file loads.
- YAML string load fails with `ValueError`:
	- The string is not valid YAML. Validate syntax (indentation, colons, lists, etc.).
- `save(...)` returns `False`:
	- Provide a valid `file_path` (or construct `YamlFile` via `read_yaml` so it knows its original path).
	- Check directory permissions; parent directories are created automatically when possible.

## Module structure

```
cores/yaml_reading_core/
├─ __init__.py          # exports YamlReadingCore, YamlFile
├─ yaml_reading_core.py # file/string loaders
├─ yaml_file.py         # YamlFile wrapper with dot‑path helpers
├─ init.yaml            # module metadata
└─ README.md            # this file
```

## See also
- GitHub API Core: lightweight repo/file fetch helpers that pair well with YAML processing
- Temp Files Manager: centralized, safe temp directory creation and cleanup