import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from app.models.database.weaviate import WeaviateUserProfile
from app.database.weaviate.client import get_weaviate_client
import weaviate.exceptions as weaviate_exceptions
import weaviate.classes as wvc
from weaviate.classes.query import Filter

logger = logging.getLogger(__name__)

class WeaviateUserOperations:
    """
    Class to handle Weaviate operations for user profiles.
    """

    def __init__(self, collection_name: str = "weaviate_user_profile"):
        self.collection_name = collection_name

    async def find_user_by_id(self, user_id: str) -> Optional[str]:
        """
        Find a user profile by user_id and return the UUID if found.
        """
        try:
            async with get_weaviate_client() as client:
                collection = client.collections.get(self.collection_name)

                response = await collection.query.fetch_objects(
                    filters=Filter.by_property("user_id").equal(user_id),
                    limit=1
                )

                if response.objects:
                    found_uuid = str(response.objects[0].uuid)
                    logger.info(f"Found existing user profile with UUID: {found_uuid}")
                    return found_uuid
                return None

        except weaviate_exceptions.WeaviateBaseError as e:
            logger.error(f"Weaviate error finding user by ID: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error finding user by ID: {str(e)}")
            return None

    async def create_user_profile(self, profile: WeaviateUserProfile, embedding_vector: List[float]) -> bool:
        """
        Create a new user profile in Weaviate.
        """
        try:
            profile_dict = self._prepare_profile_data(profile)

            async with get_weaviate_client() as client:
                collection = client.collections.get(self.collection_name)

                result = await collection.data.insert(
                    properties=profile_dict,
                    vector=embedding_vector
                )

            logger.info(f"Created user profile for {profile.github_username} with UUID: {result}")
            return True

        except weaviate_exceptions.WeaviateBaseError as e:
            logger.error(f"Weaviate error creating user profile: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating user profile: {str(e)}")
            return False

    async def update_user_profile(self, uuid: str, profile: WeaviateUserProfile, embedding_vector: List[float]) -> bool:
        """
        Update an existing user profile in Weaviate.
        """
        try:
            profile_dict = self._prepare_profile_data(profile)

            async with get_weaviate_client() as client:
                collection = client.collections.get(self.collection_name)
                await collection.data.update(
                    uuid=uuid,
                    properties=profile_dict,
                    vector=embedding_vector
                )

            logger.info(f"Updated user profile for {profile.github_username} with UUID: {uuid}")
            return True

        except weaviate_exceptions.WeaviateBaseError as e:
            logger.error(f"Weaviate error updating user profile: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating user profile: {str(e)}")
            return False

    async def upsert_user_profile(self, profile: WeaviateUserProfile, embedding_vector: List[float]) -> bool:
        """
        Create or update a user profile (upsert operation).
        """
        try:
            existing_uuid = await self.find_user_by_id(profile.user_id)

            if existing_uuid:
                logger.info(f"Updating existing profile for user_id: {profile.user_id}")
                return await self.update_user_profile(existing_uuid, profile, embedding_vector)
            else:
                logger.info(f"Creating new profile for user_id: {profile.user_id}")
                return await self.create_user_profile(profile, embedding_vector)

        except Exception as e:
            logger.error(f"Error in upsert operation: {str(e)}")
            return False

    async def search_similar_contributors(self, query_embedding: List[float], limit: int = 10, min_distance: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar contributors using vector similarity search."""
        try:
            logger.info(f"Searching for similar contributors with embedding dimension: {len(query_embedding)}")

            async with get_weaviate_client() as client:
                collection = client.collections.get(self.collection_name)

                response = await collection.query.near_vector(
                    near_vector=query_embedding,
                    limit=limit,
                    distance=min_distance,
                    return_metadata=wvc.query.MetadataQuery(distance=True)
                )

                results = []
                for obj in response.objects:
                    try:
                        properties = obj.properties
                        distance = obj.metadata.distance if obj.metadata and obj.metadata.distance else 1.0
                        similarity_score = 1.0 - distance

                        result = {
                            "user_id": properties.get("user_id"),
                            "github_username": properties.get("github_username"),
                            "display_name": properties.get("display_name"),
                            "bio": properties.get("bio"),
                            "languages": properties.get("languages", []),
                            "topics": properties.get("topics", []),
                            "followers_count": properties.get("followers_count", 0),
                            "total_stars_received": properties.get("total_stars_received", 0),
                            "similarity_score": similarity_score,
                            "distance": distance,
                            "profile_summary": properties.get("profile_text_for_embedding", "")
                        }
                        results.append(result)

                    except Exception as e:
                        logger.warning(f"Error processing search result: {str(e)}")
                        continue

                logger.info(f"Found {len(results)} similar contributors")
                return results

        except weaviate_exceptions.WeaviateBaseError as e:
            logger.error(f"Weaviate error in similarity search: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in similarity search: {str(e)}")
            return []

    async def search_contributors_by_keywords(self, keywords: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for contributors using keyword matching on profile text, languages, and topics."""
        try:
            logger.info(f"Searching for contributors with keywords: {keywords}")

            async with get_weaviate_client() as client:
                collection = client.collections.get(self.collection_name)

                keyword_query = " ".join(keywords)

                response = await collection.query.bm25(
                    query=keyword_query,
                    limit=limit,
                    return_metadata=wvc.query.MetadataQuery(score=True)
                )

                results = []
                for obj in response.objects:
                    try:
                        properties = obj.properties
                        score = obj.metadata.score if obj.metadata and obj.metadata.score else 0.0

                        result = {
                            "user_id": properties.get("user_id"),
                            "github_username": properties.get("github_username"),
                            "display_name": properties.get("display_name"),
                            "bio": properties.get("bio"),
                            "languages": properties.get("languages", []),
                            "topics": properties.get("topics", []),
                            "followers_count": properties.get("followers_count", 0),
                            "total_stars_received": properties.get("total_stars_received", 0),
                            "search_score": score,
                            "profile_summary": properties.get("profile_text_for_embedding", "")
                        }
                        results.append(result)

                    except Exception as e:
                        logger.warning(f"Error processing keyword search result: {str(e)}")
                        continue

                logger.info(f"Found {len(results)} contributors matching keywords")
                return results

        except weaviate_exceptions.WeaviateBaseError as e:
            logger.error(f"Weaviate error in keyword search: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in keyword search: {str(e)}")
            return []

    async def hybrid_search_contributors(
        self,
        query_embedding: List[float],
        keywords: List[str],
        limit: int = 10,
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining vector similarity and BM25 keyword search.
        """
        try:
            vector_results = await self.search_similar_contributors(
                query_embedding, limit
            ) if query_embedding else []

            bm25_results = await self.search_contributors_by_keywords(
                keywords, limit
            ) if keywords else []

            combined = {}

            for result in vector_results:
                user_id = result["user_id"]
                combined[user_id] = result.copy()
                combined[user_id]["vector_score"] = result.get("similarity_score", 0.0)
                combined[user_id]["bm25_score"] = 0.0
                combined[user_id]["search_method"] = "vector"

            max_bm25_score = max([r.get("search_score", 0) for r in bm25_results]) if bm25_results else 1.0

            for result in bm25_results:
                user_id = result["user_id"]
                normalized_bm25 = result.get("search_score", 0) / max_bm25_score if max_bm25_score > 0 else 0.0
                if user_id in combined:
                    combined[user_id]["bm25_score"] = normalized_bm25
                    combined[user_id]["search_method"] = "hybrid"
                else:
                    combined[user_id] = result.copy()
                    combined[user_id]["vector_score"] = 0.0
                    combined[user_id]["bm25_score"] = normalized_bm25
                    combined[user_id]["search_method"] = "bm25"

            for result in combined.values():
                result["hybrid_score"] = (
                    vector_weight * result["vector_score"] + bm25_weight * result["bm25_score"]
                )

            final_results = sorted(
                combined.values(),
                key=lambda x: x["hybrid_score"],
                reverse=True
            )[:limit]

            logger.info(f"Hybrid search returned {len(final_results)} results")
            return final_results

        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return []

    async def get_contributor_profile(self, github_username: str) -> Optional[WeaviateUserProfile]:
        """Get a specific contributor's profile by GitHub username."""
        try:
            async with get_weaviate_client() as client:
                collection = client.collections.get(self.collection_name)

                response = await collection.query.fetch_objects(
                    filters=Filter.by_property("github_username").equal(github_username),
                    limit=1
                )

                if response.objects:
                    properties = response.objects[0].properties

                    repositories = json.loads(properties.get("repositories", "[]"))
                    pull_requests = json.loads(properties.get("pull_requests", "[]"))

                    return WeaviateUserProfile(
                        user_id=properties.get("user_id"),
                        github_username=properties.get("github_username"),
                        display_name=properties.get("display_name"),
                        bio=properties.get("bio"),
                        location=properties.get("location"),
                        languages=properties.get("languages", []),
                        topics=properties.get("topics", []),
                        followers_count=properties.get("followers_count", 0),
                        following_count=properties.get("following_count", 0),
                        total_stars_received=properties.get("total_stars_received", 0),
                        total_forks=properties.get("total_forks", 0),
                        repositories=repositories,
                        pull_requests=pull_requests,
                        profile_text_for_embedding=properties.get("profile_text_for_embedding", ""),
                        last_updated=properties.get("last_updated")
                    )

                return None

        except weaviate_exceptions.WeaviateBaseError as e:
            logger.error(f"Weaviate error getting contributor profile: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting contributor profile: {str(e)}")
            return None

    def _prepare_profile_data(self, profile: WeaviateUserProfile) -> Dict[str, Any]:
        """
        Prepare profile data for Weaviate storage.
        """
        profile_dict = profile.model_dump()

        profile_dict["repositories"] = json.dumps([repo.model_dump() for repo in profile.repositories])
        profile_dict["pull_requests"] = json.dumps([pr.model_dump() for pr in profile.pull_requests])

        if isinstance(profile.last_updated, datetime):
            if profile.last_updated.tzinfo is None:
                profile.last_updated = profile.last_updated.replace(tzinfo=timezone.utc)
            profile_dict["last_updated"] = profile.last_updated.isoformat()
        else:
            profile_dict["last_updated"] = datetime.now(timezone.utc).isoformat()

        return profile_dict


async def store_user_profile(profile: WeaviateUserProfile, embedding_vector: List[float]) -> bool:
    """
    Convenience function to store or update a user profile.
    """
    operations = WeaviateUserOperations()
    return await operations.upsert_user_profile(profile, embedding_vector)

async def search_similar_contributors(query_embedding: List[float], limit: int = 10, min_distance: float = 0.7) -> List[Dict[str, Any]]:
    """
    Convenience function to search for similar contributors using vector similarity.
    """
    operations = WeaviateUserOperations()
    return await operations.search_similar_contributors(query_embedding, limit, min_distance)

async def search_contributors_by_keywords(keywords: List[str], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience function to search for contributors using keyword matching.
    """
    operations = WeaviateUserOperations()
    return await operations.search_contributors_by_keywords(keywords, limit)

async def get_contributor_profile(github_username: str) -> Optional[WeaviateUserProfile]:
    """Convenience function to get a contributor's profile by GitHub username."""
    operations = WeaviateUserOperations()
    return await operations.get_contributor_profile(github_username)

async def search_contributors(
    query_embedding: List[float],
    keywords: List[str],
    limit: int = 10,
    vector_weight: float = 0.7,
    bm25_weight: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Convenience function to perform hybrid search combining vector similarity and BM25 keyword search.
    """
    operations = WeaviateUserOperations()
    return await operations.hybrid_search_contributors(
        query_embedding, keywords, limit, vector_weight, bm25_weight
    )
