from flaskr.custom_filters import get_status_color, get_status_name
import pytest

PENDING = 1
ACCEPTED = 2
DECLINED = 3


@pytest.mark.parametrize("status,expected_color", [
    pytest.param(PENDING, "grey", id="Pending status color test"),
    pytest.param(ACCEPTED, "green", id="Accepted status color test"),
    pytest.param(DECLINED, "red", id="Declined status color test"),
])
def test_get_status_color(status, expected_color):
    result_color = get_status_color(status)
    assert result_color == expected_color


@pytest.mark.parametrize("status,expected_name", [
    pytest.param(PENDING, "Pending", id="Pending status name test"),
    pytest.param(ACCEPTED, "Accepted", id="Accepted status name test"),
    pytest.param(DECLINED, "Declined", id="Declined status name test"),
])
def test_get_status_name(status, expected_name):
    result_name = get_status_name(status)
    assert result_name == expected_name
