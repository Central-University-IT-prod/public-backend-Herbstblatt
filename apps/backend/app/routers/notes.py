from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
import pydantic
from tortoise.expressions import Q

from ..utils import auth
from db import models


router = APIRouter()


class Note(pydantic.BaseModel):
    id: UUID
    title: str
    author_name: str


@router.get("/trips/{trip_id}/notes")
async def get_notes(
    trip_id: str, user_id: Annotated[int, Depends(auth.get_user_id)]
) -> list[Note]:
    allowed_to_view = await models.User.filter(id=user_id, trips__id=trip_id).exists()
    if not allowed_to_view:
        raise HTTPException(403, "Cannot view this trip")

    notes = (
        await models.Note.filter(
            Q(visibility=models.NoteVisibility.public) | Q(owner__id=user_id),
            trip__id=trip_id,
        )
        .prefetch_related("owner")
        .all()
    )

    result = [
        Note(id=note.id, title=note.title, author_name=note.owner.name)
        for note in notes
    ]
    return result
