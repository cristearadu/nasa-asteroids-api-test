DATE_RANGES = [
    ("Valid short range", "2025-01-01", "2025-01-10", True),
    ("Mid-term range", "2024-06-01", "2024-06-15", True),
    ("Far future (no data)", "3000-01-01", "3000-01-10", False),
]

DISTANCES = [
    ("Max distance 0.05 AU", "0.05"),
    ("Max distance 0.01 AU", "0.01"),
]

INVALID_PARAMS = [
    ("Invalid param key", {"invalid": "param"}, "one or more query parameter was not recognized"),
    ("Bad date format", {"date-min": "not-a-date"}, "invalid value specified for query parameter 'date-min'"),
]

VALID_SORTING_DATES = [
    ("Valid short range", "2025-01-01", "2025-01-10")
]

EMPTY_DATE_RANGES = [
    ("Edge case empty range", "3000-01-01", "3000-01-10"),
    ("Far future no data", "3000-01-01", "3000-01-31")
]

VALID_DATA_TYPES_DATES = [
    ("Field validation range", "2024-01-01", "2024-01-10")
]
