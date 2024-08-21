from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "trip_points" DROP COLUMN "position";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "trip_points" ADD "position" INT NOT NULL;"""
