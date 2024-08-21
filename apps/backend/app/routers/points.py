from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
import pydantic

from db import models
from ..utils import auth


class Trip(pydantic.BaseModel):
    name: str


class TripPoint(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    name: str
    date_from: datetime | None
    date_to: datetime | None
    location_id: str
    location_lat: float
    location_long: float


class DBTripPoint(TripPoint):
    model_config = pydantic.ConfigDict(from_attributes=True)
    id: UUID


router = APIRouter()


@router.get("/trips/{trip_id}")
async def get_trip(
    trip_id: str, user_id: Annotated[int, Depends(auth.get_user_id)]
) -> Trip:
    allowed_to_view = await models.User.filter(id=user_id, trips__id=trip_id).exists()
    if not allowed_to_view:
        raise HTTPException(403, "Cannot view this trip")

    trip = await models.Trip.get(id=trip_id)
    return Trip(name=trip.name)


@router.get("/trips/{trip_id}/points")
async def get_points(
    trip_id: str, user_id: Annotated[int, Depends(auth.get_user_id)]
) -> list[DBTripPoint]:
    allowed_to_view = await models.User.filter(id=user_id, trips__id=trip_id).exists()
    if not allowed_to_view:
        raise HTTPException(403, "Cannot view this trip")

    points = await models.TripPoint.filter(trip__id=trip_id).order_by("date_from")
    result = [DBTripPoint.model_validate(point) for point in points]

    user = await models.User.get(id=user_id)
    user_location = DBTripPoint(
        id=uuid4(),
        name=user.location_name,
        date_from=None,
        date_to=None,
        location_id=user.location,
        location_lat=user.location_lat,
        location_long=user.location_long,
    )
    result.insert(0, user_location)
    result.append(user_location)

    return result


@router.post("/trips/{trip_id}/points", status_code=201)
async def create_point(
    trip_id: str, data: TripPoint, user_id: Annotated[int, Depends(auth.get_user_id)]
):
    allowed_to_view = await models.User.filter(id=user_id, trips__id=trip_id).exists()
    if not allowed_to_view:
        raise HTTPException(403, "Cannot view this trip")

    point = await models.TripPoint.create(**data.model_dump(), trip_id=trip_id)
    return {"status": "ok"}


@router.delete("/trips/{trip_id}/points/{point_id}")
async def delete(
    trip_id: str, point_id: str, user_id: Annotated[int, Depends(auth.get_user_id)]
):
    allowed_to_view = await models.User.filter(id=user_id, trips__id=trip_id).exists()
    if not allowed_to_view:
        raise HTTPException(403, "Cannot view this trip")

    await models.TripPoint.filter(id=point_id).delete()
    return {"status": "ok"}
