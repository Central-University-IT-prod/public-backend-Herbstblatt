from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "location_long" DOUBLE PRECISION NOT NULL;
        ALTER TABLE "users" ADD "location_lat" DOUBLE PRECISION NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "location_long";
        ALTER TABLE "users" DROP COLUMN "location_lat";"""
