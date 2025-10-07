# Postal Regex 📨

[![PyPI version](https://img.shields.io/pypi/v/postal-regex.svg)](https://pypi.org/project/postal-regex/)
[![License](https://img.shields.io/pypi/l/postal-regex)](LICENSE)
[![Build Status](https://github.com/ankitgadling/postal-regex/actions/workflows/ci.yml/badge.svg)](https://github.com/ankitgadling/postal-regex/actions)

---

A community-maintained repository of postal/ZIP code regex patterns for 50+ countries.  
Ideal for **form validation, data cleaning, and big data applications**.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Big Data Support](#big-data-support)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- ✅ 50+ countries included, with postal code regex patterns  
- ✅ Validate postal codes by **country code** or **country name**
```python
from postal_regex.core import validate

validate("IN", "110001")      # True
validate("India", "110001")   # True
validate("US", "12345-6789")  # True
````

## Examples for recently added countries (Indonesia, Bangladesh, Pakistan, Sri Lanka, Nepal)
```python

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

* ✅ Normalize country identifiers

```python
from postal_regex.core import normalize

normalize("United States")  # "US"
normalize("India")          # "IN"
```

* ✅ Works with **Pandas and Spark DataFrames**

```python
import pandas as pd
from postal_regex.bulk import validate_dataframe

df = pd.DataFrame({"country": ["US", "FR"], "postal_code": ["90210", "75001"]})
df_validated = validate_dataframe(df, country_col="country", postal_col="postal_code")
print(df_validated)
```

* ✅ JSON schema ensures consistent data structure
* ✅ Precompiled regex for fast Python validation

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

## Command-Line Usage

You can validate postal codes directly from the command line without writing any code.

### Validate Postal Codes

To validate one or more postal codes for a specific country:

```sh
python -m postal_regex.cli validate <postal_code1> <postal_code2> ... <country>
```

**Examples:**

Validate a single code for India:
```
python -m postal_regex.cli validate 110001 IN
```
Output:
```
110001: Valid
```

Validate multiple codes for the United States:
```
python -m postal_regex.cli validate 12345 90210 US
```
Output:
```
12345: Valid
90210: Valid
```

You can also use country names:
```
python -m postal_regex.cli validate 110001 India
```

### View Validation Statistics

To view local validation statistics:
```
python -m postal_regex.cli stats
```

To reset statistics:
```
python -m postal_regex.cli stats --reset
```

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
