from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "invite" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "user_id" BIGINT NOT NULL,
    "trip_id" UUID NOT NULL REFERENCES "trips" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "invite";"""
