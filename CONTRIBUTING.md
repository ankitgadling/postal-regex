---
# Contributing to Postal Regex Repository

Thank you for your interest in contributing! 
This guide will help you add new countries, maintain consistency, and ensure your contributions pass automated tests.

---

## Table of Contents

1. [Adding a New Country](#adding-a-new-country)
2. [Creating an Issue](#creating-an-issue)
3. [Submitting a Pull Request](#submitting-a-pull-request)
4. [Adding New Features](#adding-new-features)
5. [Commit Guidelines](#commit-guidelines)
6. [Testing Your Changes](#testing-your-changes)

---

## Adding a New Country

All country data is stored in `src/postal_regex/data/postal_codes.json`. Each entry must include:

* `country_code` → ISO 3166-1 alpha-2 code (2 uppercase letters)
* `country_name` → full official country name
* `postal_code_regex` → regex pattern for postal/pincode validation
* `sample_valid` → a valid postal code example for testing
* `sample_invalid` → an invalid postal code example for testing
* `local_name` → country name in local language
* `description` → brief description about postal codes

### Example Entry

```json
{
  "country_code": "DE",
  "country_name": "Germany",
  "postal_code_regex": "^[0-9]{5}$",
  "sample_valid": "10115",
  "sample_invalid": "ABCDE",
  "local_name": "Deutschland",
  "description": "German postal codes (PLZ) are five digits; the first two digits denote the region."
}
```

**Tips:**

* Keep formatting consistent with existing entries.
* Add one country per PR whenever possible for easier review.

---

## Creating an Issue

If you notice missing data, incorrect regex, or want to propose a new feature:

1. Go to the [Issues](https://github.com/ankitgadling/postal-regex/issues) tab.
2. Click **New Issue**.
3. Use a clear and descriptive title, e.g., `Add postal code regex for Japan`.
4. Include details:

   * Country name and ISO code
   * Example valid and invalid postal codes
   * Reference for regex pattern (official sources preferred)

**Example Issue:**

```
Title: Add postal code regex for Japan

Body:
Country: Japan (JP)
Sample Valid: 100-0001
Sample Invalid: ABC-123
Reference: https://www.example.com/japan-postal-codes
```

---

## Submitting a Pull Request

1. Fork the repository and create a new branch:

   ```bash
   git checkout -b add-japan-postal-code
   ```
2. Add your country entry to `src/postal_regex/data/postal_codes.json`.
3. Run Python tests locally:

   ```bash
   pytest
   ```
4. Lint your code and JSON files:

   ```bash
   flake8 .
   python -m json.tool src/postal_regex/data/postal_codes.json
   ```
5. Commit your changes using [Conventional Commits](#commit-guidelines).
6. Push your branch and create a PR against the `main` branch.

**PR Template:**

```
### Added
- Postal code regex for Japan (JP)

### Validation
- sample_valid: 100-0001
- sample_invalid: ABC-123
```

---
## Adding New Features

Contributors can propose or implement improvements beyond adding countries:

**Steps to contribute a feature:**

1. **Create an Issue** describing the feature and its purpose.
2. **Fork the repo** and create a feature branch:

```bash
git checkout -b feat/your-feature
```

3. **Implement the feature** and write tests.
4. **Format and lint** your code:

```bash
black .
flake8 .
```

5. **Commit using Conventional Commits**:

```
feat: add [short description]
```

6. **Push and open a PR** with a clear description and test results.

---

## Commit Guidelines

Use **Conventional Commits**:

| Type    | When to use                                   |
| ------- | --------------------------------------------- |
| `feat`  | Adding a new country or feature               |
| `fix`   | Correcting a regex or invalid entry           |
| `docs`  | Updating README or contribution guides        |
| `test`  | Adding or fixing test cases                   |
| `chore` | Maintenance tasks, formatting, or minor edits |

**Example Commit Messages:**

```
feat: add postal code regex for Japan (JP)
fix: correct regex for Germany (DE) postal code
docs: update contributing guide with PR instructions
test: add test case for UK postal code
```

---

## Testing Your Changes

1. Validate your regex with Python `re` module.
2. Ensure JSON is properly formatted:

```bash
python -m json.tool src/postal_regex/data/postal_codes.json
```

3. Run all tests using `pytest`:

```bash
pytest
```
---

4. **Format and lint your code** to maintain consistency and catch potential issues:

```bash
# Automatically format your code
black .

# Check for style issues, errors, and potential problems
flake8 .
```

**Notes:**

* `black` enforces consistent code formatting automatically.
* `flake8` helps catch style violations, undefined names, or other issues that `black` doesn’t fix.
* Running both ensures that your code is clean, consistent, and ready for review.

---


✅ Following this guide ensures smooth contributions, consistent formatting.

---
