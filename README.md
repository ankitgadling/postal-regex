# Postal Regex 📨

[![PyPI version](https://img.shields.io/pypi/v/postal-regex.svg)](https://pypi.org/project/postal-regex/)
[![License](https://img.shields.io/pypi/l/postal-regex)](LICENSE)
[![Build Status](https://github.com/ankitgadling/postal-regex/actions/workflows/ci.yml/badge.svg)](https://github.com/ankitgadling/postal-regex/actions)

---

A community-maintained repository of postal/ZIP code regex patterns for 50+ countries.  
Ideal for **form validation, data cleaning, and big data applications**.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [Command-Line Usage](#command-line-usage)
- [Big Data Support](#big-data-support)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

```bash
pip install postal-regex
```

For development:

```bash
git clone https://github.com/ankitgadling/postal-regex.git
cd postal-regex
pip install -e .
```

---

## Quick Start

```python
from postal_regex.core import validate

# Validate by country code
validate("IN", "110001")      # True
validate("US", "12345-6789")  # True

# By country name
validate("India", "110001")   # True

# Invalid returns False
validate("US", "ABCDE")       # False
```

---

## Features

- ✅ 50+ countries included, with postal code regex patterns
- ✅ Validate postal codes by **country code** or **country name**
- ✅ Normalize country identifiers

```python
from postal_regex.core import normalize

normalize("United States")  # "US"
normalize("India")          # "IN"
```

- ✅ Works with **Pandas and Spark DataFrames**
- ✅ JSON schema ensures consistent data structure
- ✅ Precompiled regex for fast Python validation

### Examples for Recently Added Countries (Indonesia, Bangladesh, Pakistan, Sri Lanka, Nepal)

```python
from postal_regex.core import validate

# Indonesia (ID)
validate("ID", "12345")           # **Expected: True** (valid 5-digit code)
validate("Indonesia", "12345")    # **Expected: True**

# Bangladesh (BD)
validate("BD", "1205")            # **Expected: True** (valid 4-digit code)

# Pakistan (PK)
validate("PK", "44000")           # **Expected: True** (valid 5-digit code)

# Sri Lanka (LK)
validate("LK", "00300")           # **Expected: True** (valid 5-digit code, e.g., Colombo)

# Nepal (NP)
validate("NP", "44600")           # **Expected: True** (valid 5-digit code, e.g., Kathmandu)
```

---

## Command-Line Usage

You can validate postal codes directly from the command line without writing any code.

### Validate Postal Codes

To validate one or more postal codes for a specific country:

```sh
python -m postal_regex.cli validate <postal_code1> <postal_code2> ... <country>
```

**Examples:**

Validate a single code for India:
```sh
python -m postal_regex.cli validate 110001 IN
```
Output:
```
110001: Valid
```

Validate multiple codes for the United States:
```sh
python -m postal_regex.cli validate 12345 90210 US
```
Output:
```
12345: Valid
90210: Valid
```

You can also use country names:
```sh
python -m postal_regex.cli validate 110001 India
```

### View Validation Statistics

To view local validation statistics:
```sh
python -m postal_regex.cli stats
```

To reset statistics:
```sh
python -m postal_regex.cli stats --reset
```

---

## Big Data Support

Validate postal codes in **large datasets** with Spark or Pandas.

### Spark Example

```python
from pyspark.sql import SparkSession
from postal_regex.bulk import validate_spark_dataframe

spark = SparkSession.builder.getOrCreate()
df = spark.createDataFrame([
    {"country": "FR", "postal_code": "75001"},
    {"country": "DE", "postal_code": "10115"}
])
df_validated = validate_spark_dataframe(df, country_col="country", postal_col="postal_code")
df_validated.show()
```

### Pandas Example

```python
import pandas as pd
from postal_regex.bulk import validate_dataframe

df = pd.DataFrame({
    "country": ["FR", "DE"],
    "postal_code": ["75001", "10115"]
})
df_validated = validate_dataframe(df, country_col="country", postal_col="postal_code")
print(df_validated)
```

---

## Contributing

We ❤️ contributions! Help expand coverage or improve docs.

1. Fork the repo and create a feature branch: `git checkout -b feat/new-country`.
2. Add/update patterns in `postal_regex/data/` (follow JSON schema).
3. Run tests: `pytest`.
4. Commit and push: `git commit -m "Add postal patterns for [Country]"`.
5. Open a Pull Request—reference any related issue.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines, including testing new patterns and updating examples.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

⭐ **Star this repo** if it's useful! Found a bug or missing country? [Open an issue](https://github.com/ankitgadling/postal-regex/issues). Questions? Join the discussion!
