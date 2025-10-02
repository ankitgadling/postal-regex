# Postal Regex

A community-maintained repository of postal/ZIP code regex patterns for 50+ countries. 
This package is ideal for **form validation, data cleaning, and big data applications**.

---

## Features

- ✅ 50+ countries included, with postal code regex patterns  
- ✅ Supports lookup by **country code** or **country name**  
- ✅ Precompiled regex for fast validation in Python  
- ✅ JSON schema ensures consistent data structure  
- ✅ Ready for **big data frameworks** like Spark, Dask, or Pandas  

---
## Installation

```bash
pip install postal-regex
```

## Usage

```bash
from postal_regex.core import validate, normalize, get_supported_countries

# Validate postal codes
validate("IN", "110001")          # True
validate("India", "110001")       # True
validate("US", "12345-6789")      # True

# Normalize country identifiers
normalize("India")                # "IN"
normalize("US")                   # "US"

# List all supported countries
get_supported_countries()
# [{'code': 'IN', 'name': 'India'}, {'code': 'US', 'name': 'United States'}, ...]

```
---

## Contributors

[![Contributors](https://contrib.rocks/image?repo=ankitgadling/postal-regex)](https://github.com/ankitgadling/postal-regex/graphs/contributors)

---