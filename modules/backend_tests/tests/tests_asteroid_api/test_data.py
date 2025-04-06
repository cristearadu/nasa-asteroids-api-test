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

COMBINED_DATA_AND_DISTANCE = [
    ("Combined filter short range", "2025-01-01", "2025-01-10", "0.05"),
    ("Combined filter mid-term", "2024-06-01", "2024-06-15", "0.02")
]

ABSOLUTE_MAGNITUDES = [
    ("Upper bound H=22", "22"),
    ("Upper bound H=25", "25")
]

VELOCITY_LIMITS = [
    ("v-inf ≤ 5 km/s", "5"),
    ("v-inf ≤ 10 km/s", "10")
]

DISTANCE_RANGES = [
    ("0.01 - 0.05 AU", "0.01", "0.05"),
    ("0.005 - 0.02 AU", "0.005", "0.02")
]

# min distance only
MIN_DISTANCE_VALUES = [
    ("min dist = 0.1 AU", "0.1"),
    ("min dist = 0.05 AU", "0.05")
]
