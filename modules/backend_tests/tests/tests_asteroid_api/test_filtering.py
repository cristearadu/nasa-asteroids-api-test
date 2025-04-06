import pytest

from core import ResponseKeys, AsteroidDataFields
from modules.backend_tests import AsteroidRequestBuilder
from modules.backend_tests.tests.tests_asteroid_api.test_data import DATE_RANGES, DISTANCES, COMBINED_DATA_AND_DISTANCE


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
def test_filter_by_min_distance(helper_asteroid):
    """Ensure API correctly filters results with minimum distance ≥ 0.1 AU."""
    pytest.logger.info("Filtering by dist-min = 0.1 AU")

    params = AsteroidRequestBuilder().with_dist_min("0.1").build()
    result = helper_asteroid.fetch_data(**params)

    pytest.logger.debug(f"Response received: {result}")

    assert "count" in result
    assert result["count"] >= 0  # could be 0 or more

    if result["count"] > 0:
        assert ResponseKeys.DATA.value in result
        for entry in result[ResponseKeys.DATA.value]:
            dist = float(entry[AsteroidDataFields.DIST])
            assert dist >= 0.1


@pytest.mark.filtering
@pytest.mark.flaky_regression
def test_filter_by_distance_range(helper_asteroid):
    """Verify results fall within distance range 0.01 - 0.05 AU."""
    pytest.logger.info("Filtering by dist-min=0.01 and dist-max=0.05")
    params = AsteroidRequestBuilder().with_dist_range("0.01", "0.05").build()
    result = helper_asteroid.fetch_data(**params)
    for entry in result.get(ResponseKeys.DATA.value, []):
        dist = float(entry[AsteroidDataFields.DIST])
        assert 0.01 <= dist <= 0.05


@pytest.mark.filtering
@pytest.mark.flaky_regression
def test_filter_by_absolute_magnitude_upper_bound(helper_asteroid):
    """Filter objects with absolute magnitude ≤ 22."""
    pytest.logger.info("Filtering by h <= 22")
    params = AsteroidRequestBuilder().with_h_max("22").build()
    result = helper_asteroid.fetch_data(**params)
    assert ResponseKeys.DATA.value in result


@pytest.mark.filtering
@pytest.mark.flaky_regression
def test_filter_by_velocity_upper_bound(helper_asteroid):
    """Ensure filtered objects have v-inf ≤ 5 km/s."""
    pytest.logger.info("Filtering by v-inf <= 5 km/s")
    params = AsteroidRequestBuilder().with_v_inf_max("5").build()
    result = helper_asteroid.fetch_data(**params)
    for entry in result.get(ResponseKeys.DATA.value, []):
        assert float(entry[AsteroidDataFields.V_REL]) <= 5
