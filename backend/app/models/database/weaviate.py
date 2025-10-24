from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class WeaviateRepository(BaseModel):
    """
    Represents a single repostiory within WeaviateUserProfile.
    Helps in structuring the repository-specific data that contributes to the user's overall profile
    """
    name: str = Field(..., description="The name of the repository.")
    description: Optional[str] = Field(None, description="The repository's description.")
    url: str = Field(..., description="The URL of the repository.")
    languages: List[str] = Field(..., description="The languages used in the repository.")
    stars: int = Field(0, description="The number of stars the repository has.")
    forks: int = Field(0, description="The number of forks the repository has.")

class WeaviatePullRequest(BaseModel):
    """
    Represents a single pull request created by the user.
    Provides insights into contribution patterns and collaboration style.
    """
    title: str = Field(..., description="The title of the pull request.")
    body: Optional[str] = Field(None, description="The body/description of the pull request (truncated to 500 chars).")
    state: str = Field(..., description="The state of the PR: 'open', 'closed', etc.")
    repository: str = Field(..., description="The full name of the repository (e.g., 'owner/repo').")
    created_at: Optional[str] = Field(None, description="ISO timestamp when the PR was created.")
    closed_at: Optional[str] = Field(None, description="ISO timestamp when the PR was closed (if applicable).")
    merged_at: Optional[str] = Field(None, description="ISO timestamp when the PR was merged (if applicable).")
    labels: List[str] = Field(default_factory=list, description="Labels associated with the pull request.")
    url: str = Field(..., description="The URL of the pull request.")

class WeaviateUserProfile(BaseModel):
    """
    Represents a user's profile data to be stored and indexed in Weaviate.
    Enables semantic search capabilities to find users based on their profile data.
    """
    user_id: str = Field(..., description="The unique identifier for the user, linking back to the Supabase 'users' table.")
    github_username: str = Field(..., description="The user's unique GitHub username.")
    display_name: Optional[str] = Field(None, description="User's display name.")
    bio: Optional[str] = Field(None, description="User's biography from their GitHub profile.")
    location: Optional[str] = Field(None, description="User's location.")

    repositories: List[WeaviateRepository] = Field(
        default_factory=list, description="List of repositories the user's repositories.")

    pull_requests: List[WeaviatePullRequest] = Field(
        default_factory=list, description="List of pull requests the user has created.")

    languages: List[str] = Field(default_factory=list,
                                 description="A unique, aggregated list of top 5 languages the user is most comfortable with based on usage frequency.")
    topics: List[str] = Field(default_factory=list,
                              description="A unique, aggregated list of all topics from the user's repositories.")

    followers_count: int = Field(0, description="Number of followers the user has on GitHub.")
    following_count: int = Field(0, description="Number of other users this user is following on GitHub.")
    total_stars_received: int = Field(
        0, description="Total number of stars received across all of the user's owned repositories.")
    total_forks: int = Field(0, description="Total number of times the user's repositories have been forked.")

    profile_text_for_embedding: str = Field(
        ..., description="A synthesized text field combining bio, repository names, descriptions, languages, and topics for vectorization.")

    last_updated: datetime = Field(default_factory=datetime.now,
                                   description="The date and time the profile was last updated.")

    model_config = ConfigDict(
    from_attributes = True,
    json_schema_extra = {
        "example": {
            "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
            "github_username": "jane-dev",
            "display_name": "Jane Developer",
            "bio": "Creator of innovative open-source tools. Full-stack developer with a passion for Rust and WebAssembly.",
            "location": "Berlin, Germany",
            "repositories": [
                {
                    "name": "rust-web-framework",
                    "description": "A high-performance web framework for Rust.",
                    "languages": ["Rust", "TOML"],
                    "topics": ["rust", "webdev", "performance", "framework"],
                    "stars": 2500,
                    "forks": 400
                },
                {
                    "name": "data-viz-lib",
                    "description": "A declarative data visualization library for JavaScript.",
                    "languages": ["JavaScript", "TypeScript"],
                    "topics": ["data-visualization", "d3", "charts"],
                    "stars": 1200,
                    "forks": 150
                }
            ],
            "pull_requests": [
                {
                    "title": "Add async support for database connections",
                    "body": "This PR adds comprehensive async support for database connections, improving performance by 40%...",
                    "state": "closed",
                    "repository": "microsoft/vscode",
                    "created_at": "2024-01-15T10:30:00Z",
                    "closed_at": "2024-01-20T14:20:00Z",
                    "merged_at": "2024-01-20T14:20:00Z",
                    "labels": ["enhancement", "database", "performance"],
                    "url": "https://github.com/microsoft/vscode/pull/12345",
                },
                {
                    "title": "Fix memory leak in WebAssembly module",
                    "body": "Fixes a critical memory leak that was causing crashes in production environments...",
                    "state": "open",
                    "repository": "facebook/react",
                    "created_at": "2024-02-01T09:15:00Z",
                    "closed_at": None,
                    "merged_at": None,
                    "labels": ["bug", "wasm", "critical"],
                    "url": "https://github.com/facebook/react/pull/67890",
                }
            ],
            "languages": ["Rust", "JavaScript", "TypeScript", "TOML"],
            "topics": ["rust", "webdev", "performance", "framework", "data-visualization", "d3", "charts"],
            "followers_count": 1800,
            "following_count": 250,
            "total_stars_received": 3700,
            "total_forks": 550,
            "profile_text_for_embedding": "Jane Developer, Creator of innovative open-source tools. Full-stack developer with a passion for Rust and WebAssembly. Repositories: rust-web-framework, A high-performance web framework for Rust. data-viz-lib, A declarative data visualization library for JavaScript. Languages: Rust, JavaScript, TypeScript. Topics: rust, webdev, performance, data-visualization.",
            "last_updated": "2025-06-23T12:21:00Z"
        }
    }

    )