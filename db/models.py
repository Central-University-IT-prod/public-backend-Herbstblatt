import enum
from tortoise import fields
from tortoise.models import Model

class User(Model):
    id = fields.BigIntField(pk=True)
    name = fields.TextField()
    bio = fields.TextField()
    location = fields.TextField()
    location_name = fields.TextField()
    location_lat = fields.FloatField()
    location_long = fields.FloatField()

    trips: fields.ManyToManyRelation["Trip"]

    class Meta:
        table = "users"

class Trip(Model):
    id = fields.UUIDField(pk=True)
    name = fields.TextField()
    participants: fields.ManyToManyRelation["User"] = fields.ManyToManyField("travel_agent.User", related_name="trips", through="trip_participants")
    points: fields.ReverseRelation["TripPoint"]

    class Meta:
        table = "trips"

class TripPoint(Model):
    id = fields.UUIDField(pk=True)
    name = fields.TextField()
    trip = fields.ForeignKeyField("travel_agent.Trip", related_name="points")

    date_from = fields.DatetimeField(null=True)
    date_to = fields.DatetimeField(null=True)

    location_id = fields.TextField()
    location_lat = fields.FloatField()
    location_long = fields.FloatField()

    class Meta:
        table = "trip_points"

class ChatTripInfo(Model):
    chat_id = fields.BigIntField(pk=True)
    trip: fields.ForeignKeyRelation[Trip] | None = fields.ForeignKeyField("travel_agent.Trip", related_name="chats", null=True)

class Invite(Model):
    user_id = fields.BigIntField()
    trip = fields.ForeignKeyField("travel_agent.Trip", related_name="invites")

class NoteVisibility(enum.IntEnum):
    public = 1
    private = 2

class Note(Model):
    id = fields.UUIDField(pk=True)
    chat_id = fields.BigIntField()
    message_id = fields.BigIntField()
    trip = fields.ForeignKeyField("travel_agent.Trip", related_name="notes")
    owner = fields.ForeignKeyField("travel_agent.User", related_name="notes")
    title = fields.TextField()
    visibility = fields.IntEnumField(NoteVisibility)
    text = fields.TextField()