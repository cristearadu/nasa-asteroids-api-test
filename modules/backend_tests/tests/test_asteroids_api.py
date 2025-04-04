import pytest

from test_data import *
from modules.backend_tests.general.request_builder_asteroids import AsteroidRequestBuilder
from core.constants import HTTPStatusCodes, ResponseKeys
from datetime import datetime


@pytest.mark.smoke
@pytest.mark.regression
def test_smoke(asteroid_helper):
    result = asteroid_helper.fetch_data()
    assert ResponseKeys.COUNT.value in result


@pytest.mark.regression
@pytest.mark.parametrize("label, start, end, has_data", DATE_RANGES)
def test_date_filter(asteroid_helper, label, start, end, has_data):
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = asteroid_helper.fetch_data(**params)

    count = result.get(ResponseKeys.COUNT.value, 0)
    if has_data:
        assert ResponseKeys.DATA.value in result
        assert isinstance(result[ResponseKeys.DATA.value], list)
        assert count > 0
    else:
        assert ResponseKeys.DATA.value not in result
        assert count == 0


@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.parametrize("label, param, expected_error", INVALID_PARAMS)
def test_invalid_param(asteroid_helper, label, param, expected_error):
    result = asteroid_helper.fetch_data(expected_status_code=HTTPStatusCodes.BAD_REQUEST.value, **param)
    assert expected_error in result.get("message", "")


@pytest.mark.edgecase
@pytest.mark.regression
def test_edge_case_no_data(asteroid_helper):
    params = AsteroidRequestBuilder().with_date_range("3000-01-01", "3000-01-10").build()
    result = asteroid_helper.fetch_data(**params)
    assert result.get(ResponseKeys.COUNT.value) == 0


@pytest.mark.validation
@pytest.mark.regression
@pytest.mark.parametrize("label, start, end", VALID_DATA_TYPES_DATES)
def test_data_fields_have_expected_types(asteroid_helper, label, start, end):
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = asteroid_helper.fetch_data(**params)

    data = result.get(ResponseKeys.DATA.value, [])
    assert isinstance(data, list)
    if data:
        first_entry = data[0]
        assert isinstance(first_entry[0], str)  # des
        assert isinstance(first_entry[3], str)  # cd
        assert float(first_entry[4]) >= 0       # dist


@pytest.mark.regression
@pytest.mark.parametrize("label, dist", DISTANCES)
def test_filter_by_distance(asteroid_helper, label, dist):
    params = AsteroidRequestBuilder().with_dist_max(dist).build()
    result = asteroid_helper.fetch_data(**params)
    assert ResponseKeys.DATA.value in result


@pytest.mark.validation
@pytest.mark.regression
@pytest.mark.parametrize("label, start, end", VALID_SORTING_DATES)
def test_results_sorted_by_close_approach_date(asteroid_helper, label, start, end):
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = asteroid_helper.fetch_data(**params)
    dates = [entry[3] for entry in result.get(ResponseKeys.DATA.value, [])]

    parsed_dates = [datetime.strptime(date, "%Y-%b-%d %H:%M") for date in dates]
    assert parsed_dates == sorted(parsed_dates)


@pytest.mark.edgecase
@pytest.mark.regression
@pytest.mark.parametrize("label, start, end", EMPTY_DATE_RANGES)
def test_empty_ranges_return_no_data(asteroid_helper, label, start, end):
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = asteroid_helper.fetch_data(**params)
    assert result.get(ResponseKeys.COUNT.value) == 0
    assert not result.get(ResponseKeys.DATA.value)
