# 🛰️ NASA Asteroids API – Automated Test Suite

![CI](https://github.com/cristearadu/nasa-asteroids-api-test/actions/workflows/asteroid-tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10-blue)

---

## ✅ Key Features

- 🔁 Automated nightly regression runs
- ⚙️ Manual trigger for smoke, edge cases, performance, filtering, etc.
- 🐳 Dockerized testing with mounted reports and logs
- 📊 Generates HTML + JUnit reports and GitHub summary (pass/fail circle view)
- 📦 Uploads test logs and artifacts on every run
- 🔎 Categorized test structure using `pytest.mark`
- ♻️ Retry for flaky tests
- 📁 Easy-to-navigate folder structure

---

## 🧰 Tech Stack

- Python 3.10
- Pytest + plugins
- Docker
- GitHub Actions

---

## 🚀 Getting Started

### 📦 Install Dependencies

```bash
docker build --build-arg TEST_TYPE=regression -t asteroids-api-tests .

docker run --rm \
  -e TEST_TYPE=regression \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/output:/app/output \
  asteroids-api-tests
```

### Option 2: 🧪 Local (dev use only)

```bash
pip install -r requirements.txt

pytest -m regression \
  --html=reports/report.html \
  --junitxml=reports/junit.xml
```

### ▶️ Run Tests

```bash
pytest -n auto -m regression --html=reports/report.html --junitxml=reports/junit.xml
```

To run a specific suite:

```bash
pytest -m smoke
```

---

## 🛠️ Markers Used

```ini
markers =
    smoke: Smoke tests suite to ensure API works as expected
    regression: Tests that should run in every regression/nightly cycle
    flaky_regression: Rerun flaky tests 3 times
    negative: Tests for invalid inputs and unexpected API behavior
    edgecase: Outlier conditions like extreme future date ranges
    validation: Type checking, field format validation
    filtering: Tests focused on query filters like date or distance
    performance: Simulated high-load or stress scenarios like rate limiting
```

---

## ⚙️ GitHub Actions

### Triggering

Tests run:
- ✅ On `push` to `main`
- ✅ On `pull_request` to `main`
- ✅ Every night at midnight (UTC)
- ✅ Manually (with selectable test marker)

### Outputs

- 🧪 GitHub test summary (pass/fail chart)
- 📄 JUnit and HTML reports
- 📁 Logs for each run

---

## 🧩 Design Pattern Mapping

| **Pattern**               | **File**                          | **Purpose**                                               |
|---------------------------|-----------------------------------|-----------------------------------------------------------|
| **Service Object**        | `helper_asteroids_data.py`        | Encapsulates API usage and logic for fetching asteroid data. |
| **Builder**               | `request_builder_asteroids.py`    | Dynamically constructs query parameters for test requests. |
| **Factory (Fixtures)**    | `conftest.py`                     | Generates reusable sample params and setup data.          |
| **Request Object Model**  | `asteroid_api_controller.py`      | Abstracts NASA endpoint logic into callable methods.      |
| **Layered Architecture**  | Entire project structure          | Enforces clean separation across test logic, data, and execution. |

### 🔧 Builder Design Explanation

The `AsteroidRequestBuilder()` is used as a **chainable query builder**, not a fixture.
This decision was made to:
- Keep test logic self-contained and explicit
- Allow full customization per test
- Avoid unnecessary shared state

Although fixtures could simplify usage in some scenarios, using `AsteroidRequestBuilder()` inline keeps the test intention clear. It is lightweight and does not require shared setup, so it's safe to instantiate in each test.

If builder logic grows more complex or shared prebuilt queries are needed, a fixture could be introduced in `conftest.py`.

---

## 📊 Test Suite Overview

| **Test Name**                                   | **Category**        | **File**                          | **Description**                                                                                                 |
|-------------------------------------------------|----------------------|-----------------------------------|-----------------------------------------------------------------------------------------------------------------|
| `test_cad_api_smoke_returns_basic_fields`       | Response Basics      | `test_response_basics.py`         | Ensures essential fields exist in the API CAD response                                                          |
| `test_results_sorted_by_close_approach_date`    | Response Basics      | `test_response_basics.py`         | Verifies results are sorted by close approach date                                                              |
| `test_smoke_invalid_param_returns_400`          | Error Handling       | `test_errors.py`                  | Checks invalid param returns proper 400 response                                                                |
| `test_invalid_param`                            | Error Handling       | `test_errors.py`                  | Ensures API catches unrecognized or malformed query parameters                                                  |
| `test_invalid_queries_return_400`               | Error Handling       | `test_errors.py`                  | Validates the API returns 400 on invalid `date_min`, negative `dist_max` values, and passing string to `v-inf`  |
| `test_response_schema`                          | Schema Validation    | `test_schema.py`                  | Validates response JSON matches expected schema                                                                 |
| `test_data_fields_have_expected_types`          | Schema Validation    | `test_schema.py`                  | Asserts each field type matches its defined type                                                                |
| `test_simulate_rate_limit`                      | Performance          | `test_performance.py`             | Simulates burst traffic to confirm rate limiting behavior                                                       |
| `test_smoke_valid_date_filter_returns_data`     | Filtering            | `test_filtering.py`               | Ensures valid date range returns expected asteroids                                                             |
| `test_filter_by_distance`                       | Filtering            | `test_filtering.py`               | Verifies asteroid filtering by max distance                                                                     |
| `test_combined_date_and_distance_filter`        | Filtering            | `test_filtering.py`               | Combines filters to ensure cross-parameter functionality                                                        |
| `test_filter_by_min_distance`                   | Filtering            | `test_filtering.py`               | Ensure results contain only entries with distance ≥ 0.1 AU                                                      |
| `test_filter_by_distance_range`                 | Filtering            | `test_filtering.py`               | Ensure results fall within specified min/max distance boundaries                                                |
| `test_filter_by_absolute_magnitude_upper_bound` | Filtering            | `test_filtering.py`               | Filter objects with absolute magnitude ≤ defined threshold                                                      |
| `test_filter_by_velocity_upper_bound`           | Filtering            | `test_filtering.py`               | Ensure filtered objects have v-inf ≤ defined max velocity                                                       |
| `test_edge_case_no_data`                        | Edge Case            | `test_edgecases.py`               | Confirms the API handles far future dates without failure                                                       |
| `test_empty_ranges_return_no_data`              | Edge Case            | `test_edgecases.py`               | Checks that no data is returned for truly empty valid date ranges                                               |
| `test_filter_only_planets`                      | Object Filtering     | `test_object_type_filters.py`     | Verify kind=p returns 400 since planets are not supported                                                       |
| `test_filter_only_comets`                       | Object Filtering     | `test_object_type_filters.py`     | Filter to include only comets using kind=c and a valid date range                                               |
| `test_invalid_kind_value_returns_400`           | Negative             | `test_object_type_filters.py`     | Passing an invalid `kind` param returns HTTP 400 and appropriate error                                          |
| `test_fullname_parameter_returns_full_names`    | Validation           | `test_output_format.py`           | Validates that `fullname=true` returns extended designations matching the official CAD API format               |
| `test_diameter_field_included_when_enabled`     | Validation           | `test_output_format.py`           | Ensures `diameter` field is present in results when requested (may be `None` if unknown)                        |