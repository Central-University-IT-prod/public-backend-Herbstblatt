import os
import json
import subprocess

import aiohttp
from aiogram import Router, F, types
from fluent.runtime import FluentLocalization
from tortoise.exceptions import DoesNotExist

from db.models import User, TripPoint, Trip


router = Router()


async def fetch_route(points: list[tuple[int, int]]):
    key = os.environ.get("ORS_API_KEY", "")
    async with aiohttp.ClientSession() as sess:
        async with sess.post(
            "https://api.openrouteservice.org/v2/directions/driving-car/geojson",
            json={"coordinates": points},
            headers={"Authorization": key},
        ) as resp:
            data = await resp.json()

    return data


async def save_draw(points, loc):
    route = await fetch_route(points)
    with open(loc + ".geojson", "w") as f:
        json.dump(route, f)

    subprocess.call(
        [
            "./georender/georender",
            "-i",
            loc + ".geojson",
            "-o",
            loc + ".jpg",
            "-w",
            "512",
            "-h",
            "512",
        ]
    )


@router.callback_query(F.data.startswith("show_map_"))
async def delete_trip(callback: types.CallbackQuery, strings: FluentLocalization):
    trip_id = callback.data[9:]
    try:
        user = await User.get(id=callback.from_user.id)
    except DoesNotExist:
        await callback.message.answer(strings.format_value("action-unregistered"))
        return

    has_access = await user.trips.filter(id=trip_id).exists()
    if not has_access:
        await callback.message.answer(strings.format_value("trip-no-access"))
        return

    await callback.message.answer(strings.format_value("map-drawing"))

    points = await TripPoint.filter(trip__id=trip_id).order_by("date_from")
    coords = [(p.location_long, p.location_lat) for p in points]
    coords.insert(0, (user.location_long, user.location_lat))
    coords.append((user.location_long, user.location_lat))

    path = "files/" + str(callback.message.message_id)
    await save_draw(coords, path)
    await callback.message.answer_photo(types.FSInputFile(path + ".jpg"))
    await callback.answer()

    os.remove(path + ".geojson")
    os.remove(path + ".jpg")
