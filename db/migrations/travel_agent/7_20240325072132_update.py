from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "note" ADD "trip_id" UUID NOT NULL;
        ALTER TABLE "note" ADD CONSTRAINT "fk_note_trips_f256de98" FOREIGN KEY ("trip_id") REFERENCES "trips" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "note" DROP CONSTRAINT "fk_note_trips_f256de98";
        ALTER TABLE "note" DROP COLUMN "trip_id";"""
