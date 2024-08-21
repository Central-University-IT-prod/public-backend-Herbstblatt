from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "trips" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" TEXT NOT NULL
);
        CREATE TABLE IF NOT EXISTS "chattripinfo" (
    "chat_id" BIGSERIAL NOT NULL PRIMARY KEY,
    "trip_id" UUID REFERENCES "trips" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "trip_points" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" TEXT NOT NULL,
    "position" INT NOT NULL,
    "date_from" TIMESTAMPTZ,
    "date_to" TIMESTAMPTZ,
    "location_id" TEXT NOT NULL,
    "location_lat" DOUBLE PRECISION NOT NULL,
    "location_long" DOUBLE PRECISION NOT NULL,
    "trip_id" UUID NOT NULL REFERENCES "trips" ("id") ON DELETE CASCADE
);
        ALTER TABLE "users" ADD "name" TEXT NOT NULL;
        CREATE TABLE "trip_participants" (
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "trips_id" UUID NOT NULL REFERENCES "trips" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "trip_participants";
        ALTER TABLE "users" RENAME TO "user";
        ALTER TABLE "users" DROP COLUMN "name";
        DROP TABLE IF EXISTS "chattripinfo";
        DROP TABLE IF EXISTS "trips";
        DROP TABLE IF EXISTS "trip_points";"""
