from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "note" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "chat_id" BIGINT NOT NULL,
    "message_id" BIGINT NOT NULL,
    "title" TEXT NOT NULL,
    "visibility" SMALLINT NOT NULL,
    "text" TEXT NOT NULL,
    "owner_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "note"."visibility" IS 'public: 1\nprivate: 2';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "note";"""
