from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import Optional, List
from datetime import datetime


class User(BaseModel):
    """
    Represents a user profile with various platform integrations and metadata.

    Attributes:
      id (UUID): Unique identifier for the user.
      created_at (datetime): Timestamp when the user was created.
      updated_at (datetime): Timestamp when the user was last updated.
      email (Optional[str]): Email address of the user.
      discord_id (Optional[str]): Discord user ID, if linked.
      discord_username (Optional[str]): Discord username, if linked.
      github_id (Optional[str]): GitHub user ID, if linked.
      github_username (Optional[str]): GitHub username, if linked.
      slack_id (Optional[str]): Slack user ID, if linked.
      slack_username (Optional[str]): Slack username, if linked.
      display_name (str): Display name of the user.
      avatar_url (Optional[str]): URL to the user's avatar image.
      bio (Optional[str]): Short biography or description of the user.
      location (Optional[str]): User's location.
      is_verified (bool): Indicates if the user is verified.
      verification_token (Optional[str]): Verification token for email/GitHub verification.
      verification_token_expires_at (Optional[datetime]): Expiry time for verification token.
      verified_at (Optional[datetime]): Timestamp when the user was verified.
      skills (Optional[dict]): Skills of the user.
      github_stats (Optional[dict]): GitHub statistics of the user.
      last_active_discord (Optional[datetime]): Timestamp when the user was last active on Discord.
      last_active_github (Optional[datetime]): Timestamp when the user was last active on GitHub.
      last_active_slack (Optional[datetime]): Timestamp when the user was last active on Slack.
      total_interactions_count (int): Total number of interactions.
      preferred_languages (List[str]): List of preferred programming languages.
    """
    id: UUID
    created_at: datetime
    updated_at: datetime

    email: Optional[str] = None

    discord_id: Optional[str] = None
    discord_username: Optional[str] = None
    github_id: Optional[str] = None
    github_username: Optional[str] = None
    slack_id: Optional[str] = None
    slack_username: Optional[str] = None

    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None

    is_verified: bool = False
    verification_token: Optional[str] = None
    verification_token_expires_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None

    skills: Optional[dict] = None
    github_stats: Optional[dict] = None

    last_active_discord: Optional[datetime] = None
    last_active_github: Optional[datetime] = None
    last_active_slack: Optional[datetime] = None

    total_interactions_count: int = 0
    preferred_languages: List[str] = Field(default_factory=list)


class Repository(BaseModel):
    """
    Represents a GitHub repository with metadata and indexing status.

    Attributes:
      id (UUID): Unique identifier for the repository.
      created_at (datetime): Timestamp when the repository record was created.
      updated_at (datetime): Timestamp when the repository record was last updated.
      github_id (int): GitHub's unique identifier for the repository.
      full_name (str): Full name of the repository (e.g., "owner/name").
      name (str): Name of the repository.
      owner (str): Owner of the repository.
      description (Optional[str]): Description of the repository.
      stars_count (int): Number of stars the repository has received.
      forks_count (int): Number of times the repository has been forked.
      open_issues_count (int): Number of open issues in the repository.
      languages_used (List[str]): List of programming languages used in the repository.
      topics (List[str]): List of topics/tags associated with the repository.
      is_indexed (bool): Indicates if the repository has been indexed.
      indexed_at (Optional[datetime]): Timestamp when the repository was indexed.
      indexing_status (Optional[str]): Current status of the indexing process.
      last_commit_hash (Optional[str]): Hash of the last commit indexed.
    """
    id: UUID
    created_at: datetime
    updated_at: datetime

    github_id: int
    full_name: str
    name: str
    owner: str
    description: Optional[str] = None

    stars_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0

    languages_used: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)

    is_indexed: bool = False
    indexed_at: Optional[datetime] = None
    indexing_status: Optional[str] = None
    last_commit_hash: Optional[str] = None


class Interaction(BaseModel):
    """
    Represents an interaction within a repository platform, such as a message, comment, or post.

    Attributes:
      id (UUID): Unique identifier for the interaction.
      created_at (datetime): Timestamp when the interaction was created.
      user_id (UUID): Unique identifier of the user who performed the interaction.
      repository_id (Optional[UUID]): Unique identifier of the repository associated with the interaction.
      platform (str): Name of the platform where the interaction occurred (e.g., GitHub, Slack).
      platform_specific_id (str): Platform-specific identifier for the interaction.
      channel_id (Optional[str]): Identifier for the channel where the interaction took place, if applicable.
      thread_id (Optional[str]): Identifier for the thread within the channel, if applicable.
      content (str): The textual content of the interaction.
      interaction_type (str): Type of interaction (e.g., message, comment, issue).
      sentiment_score (Optional[float]): Sentiment analysis score of the interaction content.
      intent_classification (Optional[str]): Classification of the user's intent in the interaction.
      topics_discussed (List[str]): List of topics discussed in the interaction.
      metadata (Optional[dict]): Additional metadata related to the interaction.
    """
    id: UUID
    created_at: datetime

    user_id: UUID
    repository_id: Optional[UUID] = None

    platform: str
    platform_specific_id: str
    channel_id: Optional[str] = None
    thread_id: Optional[str] = None

    content: str
    interaction_type: str

    sentiment_score: Optional[float] = None
    intent_classification: Optional[str] = None
    topics_discussed: List[str] = Field(default_factory=list)

    metadata: Optional[dict] = None


class ConversationContext(BaseModel):
    """
    Represents the user's previous interactions with the agents in a concise format as summary.

    Attributes:
      id (UUID): Unique identifier for the conversation context.
      user_id (UUID): Unique identifier of the user.
      platform (str): Platform where the conversation occurred.
      memory_thread_id (str): Unique identifier for the memory thread.
      conversation_summary (str): Summary of the conversation.
      key_topics (List[str]): List of key topics discussed in the conversation.
      total_interactions (int): Total number of interactions in the conversation.
      session_start_time (datetime): Timestamp when the conversation session started.
      session_end_time (Optional[datetime]): Timestamp when the conversation session ended.
      created_at (datetime): Timestamp when the conversation context was created.
    """
    id: UUID
    user_id: UUID

    platform: str
    memory_thread_id: str

    conversation_summary: str
    key_topics: List[str] = Field(default_factory=list)

    total_interactions: int
    session_start_time: datetime
    session_end_time: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.now)

class OrganizationIntegration(BaseModel):
    """
    Represents a registered organization (just metadata, no credentials).

    Attributes:
      id (UUID): Unique identifier for the integration.
      user_id (UUID): User/Owner who registered this organization.
      platform (str): Platform name (github, discord, slack, discourse).
      organization_name (str): Name of the organization.
      is_active (bool): Whether the integration is active.
      created_at (datetime): Timestamp when registered.
      updated_at (datetime): Timestamp when last updated.
      config (dict): Platform-specific data (org link, guild_id, etc.).
    """
    id: UUID
    user_id: UUID
    platform: str
    organization_name: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    config: Optional[dict] = None

class IndexedRepository(BaseModel):
    """Model for FalkorDB indexed repositories"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    repository_full_name: str
    graph_name: str
    indexing_status: str  # 'pending', 'completed', 'failed'
    indexed_at: Optional[datetime] = None
    indexed_by_discord_id: str
    is_deleted: bool = False
    node_count: int = 0
    edge_count: int = 0
    last_error: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
