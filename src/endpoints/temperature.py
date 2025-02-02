"""Module containing functions for interacting with temperature data from the OpenSenseMap API."""

import asyncio
from datetime import datetime, timedelta
from time import perf_counter

import requests

# avg time without sessions: 8.5 best 5 worst 32
# avg time with sessions: 2.2 best 1.8 worst 2.4
# avg time with asyncio: 1.1


async def avg_temperature():
    """
    Args:
        None

    Returns:
        Average temparature (°C) over the last hour, and a status of that temperature

    """
    start = perf_counter()
    with requests.Session() as session:
        sb_ids = get_open_sense_boxes(session)
        sb_ids = recent_sense_boxes(sb_ids)

        results = await get_all_sense_box_temps(sb_ids, session)
        avg = sum(results) / len(results)
        status = "Good"
        if avg < 10:
            status = "Too Cold"
        elif avg > 36:
            status = "Too Hot"
        stop = perf_counter()
        print(f"total time taken is {stop - start} seconds")
        return round(avg, 3), status


async def get_all_sense_box_temps(sb_ids: list, session):
    """
    Args:
        sb_ids:
          A list of SenseBox IDs to get temperatures from
        session:
          A requests.session object to make requests against

    Returns :
        A list of temperatures (°C) for sense boxes which have a valid temperature measurement.

    """
    loop = asyncio.get_event_loop()
    futures = [
        loop.run_in_executor(None, get_sense_box_temp, sb_id, session)
        for sb_id in sb_ids
    ]

    results = await asyncio.gather(*futures)
    # filter out null results
    return [float(result) for result in results if result is not None]


def get_sense_box_temp(sb_id: str, session):
    """
    Args:
        sb_id:
          ID of the sense box
        session:
          A requests.session object to make requests against

    Returns:
        The temperature (°C) for a given sense box ID.

    """
    url = "https://api.opensensemap.org/boxes/"
    start = perf_counter()

    response = session.get(url + sb_id)
    response = response.json()

    # NOTE: Add check lastMeasurement of this sensor specifically or we might return stale data
    # Loop over sensors list in the response
    for sensor in response["sensors"]:
        # If "temp" is in the title of the sensor, we can assume it is measuring temperature.
        # We also check that the lastMeasurement exists so we don't collect NoneType results
        if "temp" in sensor["title"].casefold() and sensor["lastMeasurement"]:
            stop = perf_counter()
            print(f"Api call for sb_id {sb_id} took {stop - start} seconds")
            return sensor["lastMeasurement"]["value"]

    return None


def recent_sense_boxes(sense_boxes: list):
    """
    Args:
        sense_boxes:
          A list of dicts containing sense box data from get_open_sense_boxes
    Returns:
        A list of sense box IDs, for sense boxes that have been updated in the last hour

    """
    recent_boxes = []
    start = perf_counter()

    now_str = datetime.now().isoformat(timespec="milliseconds") + "Z"
    now_dt = datetime.strptime(now_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    for sense_box in sense_boxes:
        if "lastMeasurementAt" in sense_box:
            sensor_time = sense_box["lastMeasurementAt"]
            sensor_dt = datetime.strptime(sensor_time, "%Y-%m-%dT%H:%M:%S.%fZ")

            if now_dt - sensor_dt <= timedelta(hours=1):
                recent_boxes.append(sense_box["_id"])
                
    stop = perf_counter()
    print(f"filtering outated results took {stop - start} seconds")
    return recent_boxes


def get_open_sense_boxes(session):
    """
    Args:
        session:
          A requests.session object to make requests against

    Returns:
        A list of sense boxes within the specified bounding box

    """
    url = "https://api.opensensemap.org/boxes"
    # this bounding box roughly represents WA state
    args = {"bbox": "-124,47,-121,49"}

    start = perf_counter()

    response = session.get(url, params=args)
    response = response.json()
    stop = perf_counter()
    print(f"Intial API call for boxes in the bounding box took {stop - start} seconds")

    return response
