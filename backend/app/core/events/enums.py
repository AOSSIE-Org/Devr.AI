from enum import Enum, auto
from typing import Optional, Set, Dict, List

class PlatformType(str, Enum):
    """
    Enum representing different platform types where events can originate.
    
    Each enum value is a string that matches the platform's common name.
    """
    GITHUB = "github"
    DISCORD = "discord"
    SLACK = "slack"
    DISCOURSE = "discourse"
    SYSTEM = "system"
    
    @classmethod
    def get_external_platforms(cls) -> List["PlatformType"]:
        """Returns a list of all external platforms (excluding SYSTEM)."""
        return [platform for platform in cls if platform != cls.SYSTEM]
    
    def is_external(self) -> bool:
        """Returns True if the platform is external (not SYSTEM)."""
        return self != self.SYSTEM


class EventType(str, Enum):
    """
    Enum representing different event types that can occur across platforms.
    
    Events are grouped into categories:
    - GitHub/Repository events (issue and PR related)
    - Communication events (messages, reactions)
    - System events (onboarding, knowledge management, analytics)
    """
    # GitHub/Repository events
    ISSUE_CREATED = "issue.created"
    ISSUE_CLOSED = "issue.closed"
    ISSUE_UPDATED = "issue.updated"
    ISSUE_COMMENTED = "issue.commented"
    PR_CREATED = "pr.created"
    PR_UPDATED = "pr.updated"
    PR_COMMENTED = "pr.commented"
    PR_MERGED = "pr.merged"
    PR_REVIEWED = "pr.reviewed"
    
    # Communication events
    MESSAGE_CREATED = "message.created"
    MESSAGE_UPDATED = "message.updated"
    REACTION_ADDED = "reaction.added"
    USER_JOINED = "user.joined"
    
    # System events
    ONBOARDING_STARTED = "onboarding.started"
    ONBOARDING_COMPLETED = "onboarding.completed"
    FAQ_REQUESTED = "faq.requested"
    KNOWLEDGE_UPDATED = "knowledge.updated"
    ANALYTICS_COLLECTED = "analytics.collected"
    
    @classmethod
    def get_by_prefix(cls, prefix: str) -> List["EventType"]:
        """
        Returns all events with the given prefix.
        
        Args:
            prefix: The prefix to filter by (e.g., 'issue', 'pr', 'message')
            
        Returns:
            List of EventType values matching the prefix
        """
        return [event for event in cls if event.value.startswith(f"{prefix}.")]
    
    @classmethod
    def get_platform_events(cls, platform: PlatformType) -> Set["EventType"]:
        """
        Returns the set of events applicable to a specific platform.
        
        Args:
            platform: The platform to get events for
            
        Returns:
            Set of EventType values relevant to the platform
        """
        platform_event_map: Dict[PlatformType, Set[EventType]] = {
            PlatformType.GITHUB: set(cls.get_by_prefix("issue") + cls.get_by_prefix("pr")),
            PlatformType.DISCORD: {cls.MESSAGE_CREATED, cls.MESSAGE_UPDATED, cls.REACTION_ADDED, cls.USER_JOINED},
            PlatformType.SLACK: {cls.MESSAGE_CREATED, cls.MESSAGE_UPDATED, cls.REACTION_ADDED, cls.USER_JOINED},
            PlatformType.DISCOURSE: {cls.MESSAGE_CREATED, cls.MESSAGE_UPDATED, cls.REACTION_ADDED, cls.USER_JOINED},
            PlatformType.SYSTEM: {cls.ONBOARDING_STARTED, cls.ONBOARDING_COMPLETED, cls.FAQ_REQUESTED, 
                                cls.KNOWLEDGE_UPDATED, cls.ANALYTICS_COLLECTED},
        }
        return platform_event_map.get(platform, set())
    
    def is_system_event(self) -> bool:
        """Returns True if the event is a system event."""
        return self in EventType.get_platform_events(PlatformType.SYSTEM)
