import asyncio
import logging
from backend.app.services.vector_db.service import EmbeddingItem, VectorDBService

logging.basicConfig(level=logging.INFO)

vector_db = VectorDBService()

async def test_create_table():
    success = await vector_db.create_table()
    print(f"Create table: {'Success' if success else 'Failed'}")

async def test_add_item():
    item = EmbeddingItem(
        id="test1",
        collection="test_collection",
        content="This is a test content",
        metadata={"type": "example"},
        embedding=[0.1] * 100,
    )
    success = await vector_db.add_item(item)
    print(f"Add item: {'Success' if success else 'Failed'}")

async def test_get_item():
    item = await vector_db.get_item("test1", "test_collection")
    print(f"Get item: {item}")

async def test_update_item():
    item = EmbeddingItem(
        id="test1",
        collection="test_collection",
        content="This is an updated content",
        metadata={"type": "example"},
        embedding=[0.2] * 100,
    )
    success = await vector_db.update_item(item)
    print(f"Update item: {'Success' if success else 'Failed'}")

async def test_search():
    query_embedding = [0.2] * 100
    results = await vector_db.search(query_embedding, "test_collection", limit=5)
    print(f"Search results: {results}")

async def test_list_collections():
    collections = await vector_db.list_collections()
    print(f"Collections: {collections}")

async def test_delete_item():
    success = await vector_db.delete_item("test1", "test_collection")
    print(f"Delete item: {'Success' if success else 'Failed'}")

async def test_check_connection():
    success = await vector_db.check_connection()
    print(f"Check connection: {'Success' if success else 'Failed'}")

async def run_tests():
    await test_create_table()
    await test_add_item()
    await test_get_item()
    await test_update_item()
    await test_search()
    await test_list_collections()
    await test_delete_item()
    await test_check_connection()

asyncio.run(run_tests())
