"""Module testing the temperature module."""

import json

from datetime import datetime, timedelta
import pytest
import requests
import requests_mock

from mock import patch

from hivebox.src.endpoints import temperature


def test_get_open_sense_boxes():
    """Test that we can get a list of open sense boxes."""
    with open("tests/mock_data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        session = requests.Session()

        with requests_mock.Mocker(session=session) as mock_session:
            mock_session.get("https://api.opensensemap.org/boxes", json=data)
            results = temperature.get_open_sense_boxes(session)

    # Verify type of results from function matches type of mocked data
    assert type(results) is type(data)

    # Verify length of results from function matches length of mocked data
    assert len(results) == len(data) == 9

    # Verify contents of results from function matches contents of mocked data
    assert results == data


def test_recent_sense_boxes():
    """Test that we can get a list of recently updated sense boxes."""

    now_str = datetime.now().isoformat(timespec="milliseconds") + "Z"
    now_dt = datetime.strptime(now_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    old_data_str = datetime.strftime(
        now_dt - timedelta(hours=2), "%Y-%m-%dT%H:%M:%S.%f"
    )

    mock_data = [
        {"_id": "5ad4cf6d223bd8001939172d", "lastMeasurementAt": f"{now_str}"},
        {"_id": "5ad4cf6d223bd8001939172e", "lastMeasurementAt": f"{now_str}"},
        {"_id": "5ad4cf6d223bd8001939172f", "badKey": f"{now_str}"},
        {"_id": "5ad4cf6d223bd8001939172g"},
        {"_id": "5ad4cf6d223bd8001939172h", "lastMeasurementAt": f"{old_data_str}Z"},
    ]

    results = temperature.recent_sense_boxes(mock_data)

    # Verify return type of function
    assert isinstance(results, list)

    # Verify length of results based on mocked data
    assert len(results) == 2


def test_get_sense_box_temp_good():
    """Test that an ID with a valid, recent temp measurement returns that measurement"""
    sb_id = "5ad4cf6d223bd8001939172d"
    with open(f"tests/mock_{sb_id}.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        session = requests.Session()

        with requests_mock.Mocker(session=session) as mock_session:
            mock_session.get(f"https://api.opensensemap.org/boxes/{sb_id}", json=data)
            assert temperature.get_sense_box_temp(sb_id, session) == "20.40"


def test_get_sense_box_temp_bad():
    """Test that an ID with no recent temp measurement returns None"""
    sb_id = "5ad4cfdc223bd80019392774"
    with open(f"tests/mock_{sb_id}.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        session = requests.Session()

        with requests_mock.Mocker(session=session) as mock_session:
            mock_session.get(f"https://api.opensensemap.org/boxes/{sb_id}", json=data)
            assert temperature.get_sense_box_temp(sb_id, session) is None


@pytest.mark.asyncio
@patch("hivebox.src.endpoints.temperature.get_sense_box_temp", side_effect=[10, 15])
async def test_get_all_sense_box_temps(mock_get_sense_box_temp):  # pylint: disable=unused-argument
    """Test that we can get a list of temps. Session / IDs are mocked and don't need to be valid."""  # pylint: disable=line-too-long
    session = ""
    sb_ids = ["5ad4cf6d223bd8001939172d", "5ad4cfdc223bd80019392774"]
    assert await temperature.get_all_sense_box_temps(sb_ids, session) == [10, 15]


@pytest.mark.asyncio
@patch(
    "hivebox.src.endpoints.temperature.get_all_sense_box_temps", return_value=[10, 15]
)
@patch("hivebox.src.endpoints.temperature.get_sense_box_temp", side_effect=[10, 15])
@patch(
    "hivebox.src.endpoints.temperature.recent_sense_boxes",
    side_effect=[["5ad4cf6d223bd8001939172d", "5ad4cfdc223bd80019392774"]],
)
@patch(
    "hivebox.src.endpoints.temperature.get_open_sense_boxes",
    side_effect=["box1", "box2", "box3"],
)
# pylint: disable=unused-argument
async def test_avg_temperature_good(
    mock_get_open_sense_boxes,
    mock_recent_sense_boxes,
    mock_get_sense_box_temp,
    mock_get_all_sense_box_temps,
):
    """ Test that we can get an average "Good" temperature by calling the main temperature function.
    All return values are mocked for now, though this may change.
    """
    results, status = await temperature.avg_temperature()
    assert isinstance(results, float)
    assert results == 12.5
    assert isinstance(status, str)
    assert status == "Good"


@pytest.mark.asyncio
@patch(
    "hivebox.src.endpoints.temperature.get_all_sense_box_temps", return_value=[5, 10]
)
@patch("hivebox.src.endpoints.temperature.get_sense_box_temp", side_effect=[5, 10])
@patch(
    "hivebox.src.endpoints.temperature.recent_sense_boxes",
    side_effect=[["5ad4cf6d223bd8001939172d", "5ad4cfdc223bd80019392774"]],
)
@patch(
    "hivebox.src.endpoints.temperature.get_open_sense_boxes",
    side_effect=["box1", "box2", "box3"],
)
# pylint: disable=unused-argument
async def test_avg_temperature_cold(
    mock_get_open_sense_boxes,
    mock_recent_sense_boxes,
    mock_get_sense_box_temp,
    mock_get_all_sense_box_temps,
):
    """ Test that we can get an average "Cold" temperature by calling the main temperature function.
    All return values are mocked for now, though this may change.
    """
    results, status = await temperature.avg_temperature()
    assert isinstance(results, float)
    assert results == 7.5
    assert isinstance(status, str)
    assert status == "Too Cold"


@pytest.mark.asyncio
@patch(
    "hivebox.src.endpoints.temperature.get_all_sense_box_temps", return_value=[35, 40]
)
@patch("hivebox.src.endpoints.temperature.get_sense_box_temp", side_effect=[35, 40])
@patch(
    "hivebox.src.endpoints.temperature.recent_sense_boxes",
    side_effect=[["5ad4cf6d223bd8001939172d", "5ad4cfdc223bd80019392774"]],
)
@patch(
    "hivebox.src.endpoints.temperature.get_open_sense_boxes",
    side_effect=["box1", "box2", "box3"],
)
# pylint: disable=unused-argument
async def test_avg_temperature_hot(
    mock_get_open_sense_boxes,
    mock_recent_sense_boxes,
    mock_get_sense_box_temp,
    mock_get_all_sense_box_temps,
):
    """ Test that we can get an average temperature by calling the main temperature function.
    All return values are mocked for now, though this may change.
    """
    results, status = await temperature.avg_temperature()
    assert isinstance(results, float)
    assert results == 37.5
    assert isinstance(status, str)
    assert status == "Too Hot"
