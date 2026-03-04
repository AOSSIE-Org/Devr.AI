from app.db.weaviate.weaviate_client import get_client
from datetime import datetime
from uuid import uuid4
from app.model.weaviate.models import (
    WeaviateUserProfile,
    WeaviateCodeChunk,
    WeaviateInteraction
)


def test_weaviate_client():
    client = get_client()
    assert client is not None, "Weaviate client should not be None"
    try:
        ready = client.is_ready()
        assert ready, "Weaviate client is not ready"
    except Exception as e:
        raise AssertionError(f"Weaviate client connection failed: {e}")

def insert_user_profile():
    user_profile = WeaviateUserProfile(
        supabase_user_id=str(uuid4()),
        profile_summary="Test user profile summary",
        primary_languages=["Python", "JavaScript"],
        expertise_areas=["Web Development", "Data Science"],
        embedding=[0.1] * 384  # Example embedding
    )
    client = get_client()
    try:
        client.data_object.create(
            data_object=user_profile.dict(by_alias=True),
            class_name="weaviate_user_profile"
        )
        print("User profile inserted successfully.")
        return user_profile
    except Exception as e:
        print(f"Error inserting user profile: {e}")
        return None


def get_user_profile_by_id(user_id: str):
    client = get_client()
    try:
        questions = client.collections.get("weaviate_user_profile")
        response = questions.query.bm25(
            query=user_id,
            properties=["supabaseUserId", "profileSummary", "primaryLanguages", "expertiseAreas"]
        )
        if response and len(response) > 0:
            user_profile_data = response[0]
            return WeaviateUserProfile(**user_profile_data)
    except Exception as e:
        print(f"Error retrieving user profile: {e}")
        return None

def update_user_profile(user_id: str):
    questions = get_client().collections.get("weaviate_user_profile")
    try:
        user_profile = questions.query.bm25(
            query=user_id,
            properties=["supabaseUserId", "profileSummary", "primaryLanguages", "expertiseAreas"]
        )
        if user_profile:
            user_profile[0]["profileSummary"] = "Updated profile summary"
            questions.update(user_profile[0])
            print("User profile updated successfully.")
            return user_profile[0]
        else:
            print("User profile not found.")
            return None
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return None

def delete_user_profile(user_id: str):
    questions = get_client().collections.get("weaviate_user_profile")
    try:
        deleted = questions.data.delete_by_id(user_id)
        if deleted:
            print("User profile deleted successfully.")
            return True
        else:
            print("User profile not found.")
            return False
    except Exception as e:
        print(f"Error deleting user profile: {e}")
        return False

def test_user_profile():
    inserted_user = insert_user_profile()
    assert inserted_user is not None, "User profile insertion failed"
    get_user_profile_by_id(inserted_user.supabase_user_id)
    update_user_profile(inserted_user.supabase_user_id)
    delete_user_profile(inserted_user.supabase_user_id)


def insert_code_chunk():
    client = get_client()
    code_chunk = WeaviateCodeChunk(
        supabase_chunk_id=str(uuid4()),
        code_content="def hello_world():\n    print('Hello, world!')",
        language="Python",
        function_names=["hello_world"],
        embedding=[0.1] * 384  # Example embedding
    )
    try:
        client.data_object.create(
            data_object=code_chunk.dict(by_alias=True),
            class_name="weaviate_code_chunk"
        )
        print("Code chunk inserted successfully.")
        return code_chunk
    except Exception as e:
        print(f"Error inserting code chunk: {e}")
        return None
def get_code_chunk_by_id(code_chunk_id: str):
    client = get_client()
    try:
        code_chunk = client.data_object.get(
            id=code_chunk_id,
            class_name="weaviate_code_chunk"
        )
        if code_chunk:
            return WeaviateCodeChunk(**code_chunk)
    except Exception as e:
        print(f"Error retrieving code chunk: {e}")
        return None
def update_code_chunk(code_chunk_id: str):
    client = get_client()
    try:
        code_chunk = client.data_object.get(
            id=code_chunk_id,
            class_name="weaviate_code_chunk"
        )
        if code_chunk:
            code_chunk["codeContent"] = "Updated code content"
            client.data_object.update(
                data_object=code_chunk,
                class_name="weaviate_code_chunk"
            )
            print("Code chunk updated successfully.")
            return WeaviateCodeChunk(**code_chunk)
        else:
            print("Code chunk not found.")
            return None
    except Exception as e:
        print(f"Error updating code chunk: {e}")
        return None
def delete_code_chunk(code_chunk_id: str):
    client = get_client()
    try:
        deleted = client.data_object.delete(
            id=code_chunk_id,
            class_name="weaviate_code_chunk"
        )
        if deleted:
            print("Code chunk deleted successfully.")
            return True
        else:
            print("Code chunk not found.")
            return False
    except Exception as e:
        print(f"Error deleting code chunk: {e}")
        return False
def test_code_chunk():
    inserted_chunk = insert_code_chunk()
    assert inserted_chunk is not None, "Code chunk insertion failed"
    get_code_chunk_by_id(inserted_chunk.supabase_chunk_id)
    update_code_chunk(inserted_chunk.supabase_chunk_id)
    delete_code_chunk(inserted_chunk.supabase_chunk_id)
def insert_interaction():
    client = get_client()
    interaction = WeaviateInteraction(
        supabase_interaction_id=str(uuid4()),
        conversation_summary="Test interaction summary",
        platform="Web",
        topics=["AI", "Machine Learning"],
        embedding=[0.1] * 384  # Example embedding
    )
    try:
        client.data_object.create(
            data_object=interaction.dict(by_alias=True),
            class_name="weaviate_interaction"
        )
        print("Interaction inserted successfully.")
        return interaction
    except Exception as e:
        print(f"Error inserting interaction: {e}")
        return None

def get_interaction_by_id(interaction_id: str):
    client = get_client()
    try:
        interaction = client.data_object.get(
            id=interaction_id,
            class_name="weaviate_interaction"
        )
        if interaction:
            return WeaviateInteraction(**interaction)
    except Exception as e:
        print(f"Error retrieving interaction: {e}")
        return None
def update_interaction(interaction_id: str):
    client = get_client()
    try:
        interaction = client.data_object.get(
            id=interaction_id,
            class_name="weaviate_interaction"
        )
        if interaction:
            interaction["conversationSummary"] = "Updated interaction summary"
            client.data_object.update(
                data_object=interaction,
                class_name="weaviate_interaction"
            )
            print("Interaction updated successfully.")
            return WeaviateInteraction(**interaction)
        else:
            print("Interaction not found.")
            return None
    except Exception as e:
        print(f"Error updating interaction: {e}")
        return None
def delete_interaction(interaction_id: str):
    client = get_client()
    try:
        deleted = client.data_object.delete(
            id=interaction_id,
            class_name="weaviate_interaction"
        )
        if deleted:
            print("Interaction deleted successfully.")
            return True
        else:
            print("Interaction not found.")
            return False
    except Exception as e:
        print(f"Error deleting interaction: {e}")
        return False

def test_interaction():
    inserted_interaction = insert_interaction()
    assert inserted_interaction is not None, "Interaction insertion failed"
    get_interaction_by_id(inserted_interaction.supabase_interaction_id)
    update_interaction(inserted_interaction.supabase_interaction_id)
    delete_interaction(inserted_interaction.supabase_interaction_id)

def all_tests():
    test_weaviate_client()
    test_user_profile()
    test_code_chunk()
    test_interaction()
