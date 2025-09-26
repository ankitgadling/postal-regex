# Postal Regex Repository

A community-maintained repository of postal/ZIP code regex patterns for 25+ countries, with auto-generated tests and schema validation.  
This project is ideal for **form validation, data cleaning, and big data applications**.

---

## Features

- ✅ 25+ countries included, with postal code regex patterns  
- ✅ Supports lookup by **country code** or **country name**  
- ✅ Precompiled regex for fast validation in Python  
- ✅ Auto-generated tests using `sample_valid` and `sample_invalid` entries  
- ✅ JSON schema ensures consistent data structure  
- ✅ Ready for **big data frameworks** like Spark, Dask, or Pandas  

---
## Installation

```bash
pip install postal-regex
```

## Usage

```bash
from postal_regex.validator import validate, normalize, get_supported_countries

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