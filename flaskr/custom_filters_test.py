from flaskr.custom_filters import getStatusColor, getStatusName
import pytest


@pytest.mark.parametrize("status,expected_color", [
    pytest.param(1, "grey", id="Pending status color test"),
    pytest.param(2, "green", id="Accepted status color test"),
    pytest.param(3, "red", id="Declined status color test"),
])
def test_getStatusColor(status, expected_color):
    result_color = getStatusColor(status)
    assert result_color == expected_color


@pytest.mark.parametrize("status,expected_name", [
    pytest.param(1, "Pending", id="Pending status name test"),
    pytest.param(2, "Accepted", id="Accepted status name test"),
    pytest.param(3, "Declined", id="Declined status name test"),
])
def test_getStatusName(status, expected_name):
    result_name = getStatusName(status)
    assert result_name == expected_name
