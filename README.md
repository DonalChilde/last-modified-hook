# last_modified_hook

[![PyPI - Version](https://img.shields.io/pypi/v/last-modified-hook.svg)](https://pypi.org/project/last-modified-hook)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/last-modified-hook.svg)](https://pypi.org/project/last-modified-hook)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install last-modified-hook
```

```yaml
# add to pre-commit-config.yaml
repos:
  -  repo: https://github.com/DonalChilde/last-modified-hook
     rev: v0.0.1
     hooks:
     -  id: last-modified
        args: [--seconds, 60, --line-limit, -1]
```

## License

`last-modified-hook` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
