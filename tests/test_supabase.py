from ..backend.app.models.database.supabase import User, Interaction, CodeChunk, Repository
from uuid import uuid4
from ..backend.app.database.supabase.client import get_supabase_client
from datetime import datetime  # Your User model import

client = get_supabase_client()

def insert_user_into_supabase(user: User):
    # Convert Pydantic User model to dict to send to Supabase
    user_dict = user.dict()

    # Supabase expects datetime fields as ISO 8601 strings
    # Convert datetime fields to ISO strings
    for key in ['created_at', 'updated_at', 'verified_at', 'last_active_discord', 'last_active_github', 'last_active_slack']:
        if user_dict.get(key):
            user_dict[key] = user_dict[key].isoformat()

    response = client.table("users").insert(user_dict).execute()  # type: ignore

    if response.status_code != 201:
        raise Exception(f"Failed to insert user: {response}")
    return response.data[0]

def test_create_and_save_user():
    user = User(
        id=str(uuid4()),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        discord_id="1234567890",
        discord_username="discordUser#1234",
        github_id="987654321",
        github_username="githubUser",
        slack_id="U12345678",
        slack_username="slackUser",
        display_name="John Doe",
        email="john.doe@example.com",
        avatar_url="https://example.com/avatar.jpg",
        bio="Software developer and open source enthusiast.",
        location="San Francisco, CA",
        is_verified=True,
        verification_token="verif_token_abc123",
        verified_at=datetime.utcnow(),
        skills=["Python", "Go", "Docker"],
        github_stats={"repos": 42, "followers": 100},
        last_active_discord=datetime.utcnow(),
        last_active_github=datetime.utcnow(),
        last_active_slack=datetime.utcnow(),
        total_interactions_count=256,
        preferred_languages=["Python", "JavaScript", "Rust"],
        weaviate_user_id="weaviate-uuid-1234"
    )

    saved_user = insert_user_into_supabase(user)
    print("User saved:", saved_user)

def get_user_by_id(user_id: str):
    response = client.table("users").select("*").eq("id", user_id).execute()
    if response.status_code != 200:
        raise Exception(f"Failed to fetch user: {response}")
    if not response.data:
        raise ValueError(f"No user found with ID: {user_id}")
    return response.data[0]

def update_user(user_id: str, updates: dict):
    response = client.table("users").update(updates).eq("id", user_id).execute()
    if response.status_code != 200:
        raise Exception(f"Failed to update user: {response}")
    return response.data[0]

def delete_user(user_id: str):
    response = client.table("users").delete().eq("id", user_id).execute()
    if response.status_code != 200:
        raise Exception(f"Failed to delete user: {response}")
    return response.data[0]

# Test the user creation and saving functionality
def test_user():
    user = User(
        id=str(uuid4()),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        discord_id="1234567890",
        discord_username="discordUser#1234",
        github_id="987654321",
        github_username="githubUser",
        slack_id="U12345678",
        slack_username="slackUser",
        display_name="John Doe",
        email="john.doe@example.com",
        avatar_url="https://example.com/avatar.jpg",
        bio="Software developer and open source enthusiast.",
        location="San Francisco, CA",
        is_verified=True,
        verification_token="verif_token_abc123",
        verified_at=datetime.utcnow(),
        skills=["Python", "Go", "Docker"],
        github_stats={"repos": 42, "followers": 100},
        last_active_discord=datetime.utcnow(),
        last_active_github=datetime.utcnow(),
        last_active_slack=datetime.utcnow(),
        total_interactions_count=256,
        preferred_languages=["Python", "JavaScript", "Rust"],
        weaviate_user_id="weaviate-uuid-1234"
    )
    inserted_user = insert_user_into_supabase(user)
    print(f"Inserted User: {inserted_user}")
    get_user = get_user_by_id(inserted_user['id'])
    print(f"Fetched User: {get_user}")
    updated_user = update_user(inserted_user['id'], {"display_name": "John Updated"})
    print(f"Updated User: {updated_user}")
    deleted_user = delete_user(inserted_user['id'])
    print(f"Deleted User: {deleted_user}")


def insert_interaction(interaction: Interaction):
    interaction_dict = interaction.dict()
    for key in ['created_at', 'updated_at']:
        if interaction_dict.get(key):
            interaction_dict[key] = interaction_dict[key].isoformat()

    response = client.table("interactions").insert(interaction_dict).execute()

    if response.status_code != 201:
        raise Exception(f"Failed to insert interaction: {response}")
    return response.data[0]

def read_interaction_by_id(interaction_id: str):
    response = client.table("interactions").select("*").eq("id", interaction_id).execute()
    if response.status_code != 200:
        raise Exception(f"Failed to fetch interaction: {response}")
    if not response.data:
        raise ValueError(f"No interaction found with ID: {interaction_id}")
    return response.data[0]

def update_interaction(interaction_id: str, updates: dict):
    response = client.table("interactions").update(updates).eq("id", interaction_id).execute()
    if response.status_code != 200:
        raise Exception(f"Failed to update interaction: {response}")
    return response.data[0]
def delete_interaction(interaction_id: str):
    response = client.table("interactions").delete().eq("id", interaction_id).execute()
    if response.status_code != 200:
        raise Exception(f"Failed to delete interaction: {response}")
    return response.data[0]

def test_interaction():
    interaction = Interaction(
        id=str(uuid4()),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        user_id=str(uuid4()),
        repository_id=str(uuid4()),
        interaction_type="comment",
        content="Hello, this is a test interaction.",
        metadata={"source": "test_script"},
        platform="github",
        platform_specific_id="gh-interaction-5678",
        weaviate_interaction_id="weaviate-interaction-1234"
    )
    inserted_interaction = insert_interaction(interaction)
    print(f"Inserted Interaction: {inserted_interaction}")
    get_interaction = read_interaction_by_id(inserted_interaction['id'])
    print(f"Fetched Interaction: {get_interaction}")
    updated_interaction = update_interaction(inserted_interaction['id'], {"content": "Updated interaction content."})
    print(f"Updated Interaction: {updated_interaction}")
    deleted_interaction = delete_interaction(inserted_interaction['id'])
    print(f"Deleted Interaction: {deleted_interaction}")

def insert_code_chunk(code_chunk: CodeChunk):
    code_chunk_dict = code_chunk.dict()
    for key in ['created_at']:
        if code_chunk_dict.get(key):
            code_chunk_dict[key] = code_chunk_dict[key].isoformat()

    response = client.table("code_chunks").insert(code_chunk_dict).execute()

    if response.status_code != 201:
        raise Exception(f"Failed to insert code chunk: {response}")
    return response.data[0]
def read_code_chunk_by_id(code_chunk_id: str):
    response = client.table("code_chunks").select("*").eq("id", code_chunk_id).execute()
    if response.status_code != 200:
        raise Exception(f"Failed to fetch code chunk: {response}")
    if not response.data:
        raise ValueError(f"No code chunk found with ID: {code_chunk_id}")
    return response.data[0]
def update_code_chunk(code_chunk_id: str, updates: dict):
    response = client.table("code_chunks").update(updates).eq("id", code_chunk_id).execute()
    if response.status_code != 200:
        raise Exception(f"Failed to update code chunk: {response}")
    return response.data[0]
def delete_code_chunk(code_chunk_id: str):
    response = client.table("code_chunks").delete().eq("id", code_chunk_id).execute()
    if response.status_code != 200:
        raise Exception(f"Failed to delete code chunk: {response}")
    return response.data[0]
def test_code_chunk():
    code_chunk = CodeChunk(
        id=str(uuid4()),
        repository_id=str(uuid4()),
        created_at=datetime.utcnow(),
        file_path="/path/to/file.py",
        file_name="file.py",
        file_extension=".py",
        chunk_index=1,
        content="def hello_world():\n    print('Hello, world!')",
        chunk_type="function",
        language="Python",
        lines_start=1,
        lines_end=3,
        code_metadata={"complexity": "low"},
        weaviate_chunk_id="weaviate-chunk-1234"
    )
    inserted_code_chunk = insert_code_chunk(code_chunk)
    print(f"Inserted Code Chunk: {inserted_code_chunk}")
    get_code_chunk = read_code_chunk_by_id(inserted_code_chunk['id'])
    print(f"Fetched Code Chunk: {get_code_chunk}")
    updated_code_chunk = update_code_chunk(inserted_code_chunk['id'], {
        "content": "def hello_world():\n    print('Updated content!')"})
    print(f"Updated Code Chunk: {updated_code_chunk}")
    deleted_code_chunk = delete_code_chunk(inserted_code_chunk['id'])
    print(f"Deleted Code Chunk: {deleted_code_chunk}")
def insert_repository(repository: Repository):
    repository_dict = repository.dict()
    for key in ['created_at', 'updated_at', 'indexed_at']:
        if repository_dict.get(key):
            repository_dict[key] = repository_dict[key].isoformat()

    response = client.table("repositories").insert(repository_dict).execute()

    if response.status_code != 201:
        raise Exception(f"Failed to insert repository: {response}")
    return response.data[0]
def read_repository_by_id(repository_id: str):
    response = client.table("repositories").select("*").eq("id", repository_id).execute()
    if response.status_code != 200:
        raise Exception(f"Failed to fetch repository: {response}")
    if not response.data:
        raise ValueError(f"No repository found with ID: {repository_id}")
    return response.data[0]
def update_repository(repository_id: str, updates: dict):
    response = client.table("repositories").update(updates).eq("id", repository_id).execute()
    if response.status_code != 200:
        raise Exception(f"Failed to update repository: {response}")
    return response.data[0]
def delete_repository(repository_id: str):
    response = client.table("repositories").delete().eq("id", repository_id).execute()
    if response.status_code != 200:
        raise Exception(f"Failed to delete repository: {response}")
    return response.data[0]
def test_repository():
    repository = Repository(
        id=str(uuid4()),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        github_id=123456789,
        full_name="example/repo",
        name="repo",
        owner="example",
        description="An example repository for testing.",
        stars_count=100,
        forks_count=10,
        open_issues_count=5,
        language="Python",
        topics=["example", "test"],
        is_indexed=True,
        indexed_at=datetime.utcnow(),
        indexing_status="completed",
        total_chunks_count=50,
        last_commit_hash="abc123def456",
        indexing_progress={"current": 50, "total": 100},
        weaviate_repo_id="weaviate-repo-1234"
    )
    inserted_repository = insert_repository(repository)
    print(f"Inserted Repository: {inserted_repository}")
    get_repository = read_repository_by_id(inserted_repository['id'])
    print(f"Fetched Repository: {get_repository}")
    updated_repository = update_repository(inserted_repository['id'], {"description": "Updated description."})
    print(f"Updated Repository: {updated_repository}")
    deleted_repository = delete_repository(inserted_repository['id'])
    print(f"Deleted Repository: {deleted_repository}")

def all_tests():
    test_user()
    test_interaction()
    test_code_chunk()
    test_repository()
