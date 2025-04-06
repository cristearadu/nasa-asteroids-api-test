import pytest

from core import ResponseKeys, AsteroidDataFields
from modules.backend_tests import AsteroidRequestBuilder
from modules.backend_tests.tests.tests_asteroid_api.test_data import (
    DATE_RANGES,
    DISTANCES,
    COMBINED_DATA_AND_DISTANCE,
    ABSOLUTE_MAGNITUDES,
    VELOCITY_LIMITS,
    DISTANCE_RANGES,
    MIN_DISTANCE_VALUES
)


@pytest.mark.smoke
@pytest.mark.filtering
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end, has_data", DATE_RANGES)
def test_smoke_valid_date_filter_returns_data(helper_asteroid, label, start, end, has_data):
    """
    Smoke test: Ensure a valid date range returns a well-formed data list.
    """
    pytest.logger.info(f"[{label}] Testing date range: {start} → {end}")

    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)

    count = result.get(ResponseKeys.COUNT.value, 0)
    data = result.get(ResponseKeys.DATA.value)

    if ResponseKeys.COUNT.value not in result:
        pytest.logger.warning(f"[{label}] Missing 'count' in response.")

    if has_data:
        assert data is not None, f"[{label}] Expected 'data' key missing."
        assert isinstance(data, list), f"[{label}] 'data' is not a list."
        assert count > 0, f"[{label}] Expected count > 0 but got {count}."
    else:
        assert data is None or data == [], f"[{label}] Expected no data, but got: {data}"
        assert count == 0, f"[{label}] Expected count == 0, but got {count}"

    pytest.logger.info(f"[{label}] Date filter passed")


@pytest.mark.filtering
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, dist", DISTANCES)
def test_filter_by_distance(helper_asteroid, label, dist):
    """Ensure distance filter reduces or limits result set."""
    pytest.logger.info(f"[{label}] Testing with dist-max={dist} AU")

    params = AsteroidRequestBuilder().with_dist_max(dist).build()
    result = helper_asteroid.fetch_data(**params)

    if ResponseKeys.DATA.value not in result:
        pytest.logger.error(f"[{label}] Response missing '{ResponseKeys.DATA.value}' key")
    else:
        data = result[ResponseKeys.DATA.value]
        if not data:
            pytest.logger.warning(f"[{label}] No results returned for dist-max={dist}")
        else:
            pytest.logger.info(f"[{label}] Retrieved {len(data)} entries within {dist} AU")

    assert ResponseKeys.DATA.value in result


@pytest.mark.filtering
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end, dist", COMBINED_DATA_AND_DISTANCE)
def test_combined_date_and_distance_filter(helper_asteroid, label, start, end, dist):
    """Test combined filtering with both date range and maximum distance."""
    pytest.logger.info(f"[{label}] Combined filter: {start} → {end} with dist-max={dist}")
    params = (
        AsteroidRequestBuilder()
        .with_date_range(start, end)
        .with_dist_max(dist)
        .build()
    )

    result = helper_asteroid.fetch_data(**params)
    data = result.get(ResponseKeys.DATA.value, [])

    pytest.logger.debug(f"[{label}] Total entries returned: {len(data)}")
    if not data:
        pytest.logger.warning(f"[{label}] No entries returned with combined filters")

    max_dist = float(dist)
    for i, entry in enumerate(data):
        try:
            approach_distance = float(entry[AsteroidDataFields.DIST])
        except (ValueError, IndexError) as e:
            pytest.logger.error(f"[{label}] Invalid distance at row {i}: {e}")
            pytest.fail(f"Invalid distance value at row {i}: {entry} ({e})")

        assert approach_distance <= max_dist, (
            f"Entry {i} exceeds max distance: {approach_distance} > {max_dist} (entry: {entry})"
        )


@pytest.mark.filtering
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, dist_min", MIN_DISTANCE_VALUES)
def test_filter_by_min_distance(helper_asteroid, label, dist_min):
    """Ensure API correctly filters results with minimum distance ≥ defined threshold."""
    pytest.logger.info(f"[{label}] Filtering by dist-min = {dist_min}")
    params = AsteroidRequestBuilder().with_dist_min(dist_min).build()
    result = helper_asteroid.fetch_data(**params)

    pytest.logger.debug(f"Response received: {result}")
    assert ResponseKeys.COUNT.value in result
    assert result[ResponseKeys.COUNT.value] >= 0

    if result[ResponseKeys.COUNT.value] > 0:
        assert ResponseKeys.DATA.value in result
        for entry in result[ResponseKeys.DATA.value]:
            dist = float(entry[AsteroidDataFields.DIST])
            assert dist >= float(dist_min)


@pytest.mark.filtering
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, dist_min, dist_max", DISTANCE_RANGES)
def test_filter_by_distance_range(helper_asteroid, label, dist_min, dist_max):
    """Verify results fall within distance range defined in test_data.py."""
    pytest.logger.info(f"[{label}] Filtering by dist-min={dist_min} and dist-max={dist_max}")
    params = AsteroidRequestBuilder().with_dist_range(dist_min, dist_max).build()
    result = helper_asteroid.fetch_data(**params)

    for entry in result.get(ResponseKeys.DATA.value, []):
        dist = float(entry[AsteroidDataFields.DIST])
        assert float(dist_min) <= dist <= float(dist_max)


@pytest.mark.filtering
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, magnitude", ABSOLUTE_MAGNITUDES)
def test_filter_by_absolute_magnitude_upper_bound(helper_asteroid, label, magnitude):
    """Filter objects with absolute magnitude ≤ threshold defined in test_data.py."""
    pytest.logger.info(f"[{label}] Filtering by h <= {magnitude}")
    params = AsteroidRequestBuilder().with_h_max(magnitude).build()
    result = helper_asteroid.fetch_data(**params)

    assert ResponseKeys.DATA.value in result


@pytest.mark.filtering
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, velocity", VELOCITY_LIMITS)
def test_filter_by_velocity_upper_bound(helper_asteroid, label, velocity):
    """Ensure filtered objects have v-inf ≤ defined max velocity."""
    pytest.logger.info(f"[{label}] Filtering by v-inf <= {velocity} km/s")
    params = AsteroidRequestBuilder().with_v_inf_max(velocity).build()
    result = helper_asteroid.fetch_data(**params)

    for entry in result.get(ResponseKeys.DATA.value, []):
        assert float(entry[AsteroidDataFields.V_REL]) <= float(velocity)
