import asyncio
from app.database.weaviate.client import get_client
import weaviate.classes.config as wc

async def create_schema(client, name, properties):
    await client.collections.create(
        name=name,
        properties=properties,
        vectorizer_config=wc.Configure.Vectorizer.none()
    )
    print(f"Created: {name}")

async def create_user_profile_schema(client):
    """
    Create schema for WeaviateUserProfile model.
    Main vectorization will be on profile_text_for_embedding field.
    """
    properties = [
        wc.Property(name="user_id", data_type=wc.DataType.TEXT),
        wc.Property(name="github_username", data_type=wc.DataType.TEXT),
        wc.Property(name="display_name", data_type=wc.DataType.TEXT),
        wc.Property(name="bio", data_type=wc.DataType.TEXT),
        wc.Property(name="location", data_type=wc.DataType.TEXT),
        wc.Property(name="repositories", data_type=wc.DataType.TEXT),  # JSON string
        wc.Property(name="pull_requests", data_type=wc.DataType.TEXT),  # JSON string
        wc.Property(name="languages", data_type=wc.DataType.TEXT_ARRAY),
        wc.Property(name="topics", data_type=wc.DataType.TEXT_ARRAY),
        wc.Property(name="followers_count", data_type=wc.DataType.INT),
        wc.Property(name="following_count", data_type=wc.DataType.INT),
        wc.Property(name="total_stars_received", data_type=wc.DataType.INT),
        wc.Property(name="total_forks", data_type=wc.DataType.INT),
        wc.Property(name="profile_text_for_embedding", data_type=wc.DataType.TEXT),
        wc.Property(name="last_updated", data_type=wc.DataType.DATE),
    ]
    await create_schema(client, "weaviate_user_profile", properties)

async def create_all_schemas():
    """
    Create only the user profile schema as per the model structure.
    """
    client = get_client()
    try:
        await client.connect()
        await create_user_profile_schema(client)
        print("✅ User profile schema created successfully.")
    except Exception as e:
        print(f"❌ Error creating schema: {str(e)}")
        raise
    finally:
        await client.close()

def main():
    """Entry point for running the schema creation."""
    asyncio.run(create_all_schemas())


