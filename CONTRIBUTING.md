# Contributing to Postal Regex Repository

Thank you for your interest in contributing! 🎉  
This guide will help you add new countries, maintain consistency, and ensure your contributions pass automated tests.

---

## Adding a New Country

All country data is stored in `data/postal_codes.json`. Each entry must include:

- `country_code` → ISO 3166-1 alpha-2 code (2 uppercase letters)
- `country_name` → full official country name
- `postal_code_regex` → regex pattern for postal/pincode validation
- `sample_valid` → a valid postal code example for testing
- `sample_invalid` → an invalid postal code example for testing

### Example Entry:
```json
{
  "country_code": "DE",
  "country_name": "Germany",
  "postal_code_regex": "^[0-9]{5}$",
  "sample_valid": "10115",
  "sample_invalid": "ABCDE"
}
```
Note: Always verify the regex works for common valid and invalid cases.