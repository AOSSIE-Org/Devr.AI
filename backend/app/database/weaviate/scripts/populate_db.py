import json
import asyncio
from datetime import datetime
from app.database.weaviate.client import get_weaviate_client

async def populate_weaviate_user_profile(client):
    """
    Populate WeaviateUserProfile collection with sample data matching the model structure.
    """
    current_time = datetime.now().astimezone()

    user_profiles = [
        {
            "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
            "github_username": "jane-dev",
            "display_name": "Jane Developer",
            "bio": ("Creator of innovative open-source tools. Full-stack developer "
                    "with a passion for Rust and WebAssembly."),
            "location": "Berlin, Germany",
            "repositories": json.dumps([
                {
                    "name": "rust-web-framework",
                    "description": "A high-performance web framework for Rust.",
                    "url": "https://github.com/jane-dev/rust-web-framework",
                    "languages": ["Rust", "TOML"],
                    "stars": 2500,
                    "forks": 400
                },
                {
                    "name": "data-viz-lib",
                    "description": "A declarative data visualization library for JavaScript.",
                    "url": "https://github.com/jane-dev/data-viz-lib",
                    "languages": ["JavaScript", "TypeScript"],
                    "stars": 1200,
                    "forks": 150
                }
            ]),
            "pull_requests": json.dumps([
                {
                    "title": "Add async support for database connections",
                    "body": ("This PR adds comprehensive async support for database "
                             "connections, improving performance by 40%..."),
                    "state": "closed",
                    "repository": "microsoft/vscode",
                    "created_at": "2024-01-15T10:30:00Z",
                    "closed_at": "2024-01-20T14:20:00Z",
                    "merged_at": "2024-01-20T14:20:00Z",
                    "labels": ["enhancement", "database", "performance"],
                    "url": "https://github.com/microsoft/vscode/pull/12345"
                }
            ]),
            "languages": ["Rust", "JavaScript", "TypeScript", "TOML"],
            "topics": ["rust", "webdev", "performance", "framework",
                       "data-visualization", "d3", "charts"],
            "followers_count": 1800,
            "following_count": 250,
            "total_stars_received": 3700,
            "total_forks": 550,
            "profile_text_for_embedding": (
                "Jane Developer, Creator of innovative open-source tools. "
                "Full-stack developer with a passion for Rust and WebAssembly. "
                "Repositories: rust-web-framework, A high-performance web framework for Rust. "
                "data-viz-lib, A declarative data visualization library for JavaScript. "
                "Languages: Rust, JavaScript, TypeScript. "
                "Topics: rust, webdev, performance, data-visualization."
            ),
            "last_updated": current_time.isoformat()
        },
        {
            "user_id": "b2c3d4e5-f6g7-8901-2345-678901bcdefg",
            "github_username": "python-ninja",
            "display_name": "Alex Chen",
            "bio": "Python enthusiast and machine learning researcher. Building the future of AI.",
            "location": "San Francisco, CA",
            "repositories": json.dumps([
                {
                    "name": "ml-toolkit",
                    "description": "A comprehensive machine learning toolkit for Python.",
                    "url": "https://github.com/python-ninja/ml-toolkit",
                    "languages": ["Python", "Jupyter Notebook"],
                    "stars": 3200,
                    "forks": 580
                },
                {
                    "name": "data-pipeline",
                    "description": "Scalable data processing pipeline for big data applications.",
                    "url": "https://github.com/python-ninja/data-pipeline",
                    "languages": ["Python", "SQL"],
                    "stars": 1800,
                    "forks": 320
                }
            ]),
            "pull_requests": json.dumps([
                {
                    "title": "Implement advanced ML algorithms",
                    "body": ("Adding support for advanced machine learning algorithms "
                             "including neural networks..."),
                    "state": "open",
                    "repository": "tensorflow/tensorflow",
                    "created_at": "2024-02-01T09:15:00Z",
                    "closed_at": None,
                    "merged_at": None,
                    "labels": ["enhancement", "ml", "algorithms"],
                    "url": "https://github.com/tensorflow/tensorflow/pull/67890"
                }
            ]),
            "languages": ["Python", "SQL", "Jupyter Notebook"],
            "topics": ["machine-learning", "ai", "data-science", "python", "big-data"],
            "followers_count": 2400,
            "following_count": 180,
            "total_stars_received": 5000,
            "total_forks": 900,
            "profile_text_for_embedding": (
                "Alex Chen, Python enthusiast and machine learning researcher. "
                "Building the future of AI. "
                "Repositories: ml-toolkit, A comprehensive machine learning toolkit for Python. "
                "data-pipeline, Scalable data processing pipeline for big data applications. "
                "Languages: Python, SQL. "
                "Topics: machine-learning, ai, data-science, python."
            ),
            "last_updated": current_time.isoformat()
        },
        {
            "user_id": "c3d4e5f6-g7h8-9012-3456-789012cdefgh",
            "github_username": "go-developer",
            "display_name": "Sam Rodriguez",
            "bio": "Cloud infrastructure engineer specializing in Go and Kubernetes.",
            "location": "Austin, TX",
            "repositories": json.dumps([
                {
                    "name": "k8s-operator",
                    "description": "Custom Kubernetes operator for managing microservices.",
                    "url": "https://github.com/go-developer/k8s-operator",
                    "languages": ["Go", "Dockerfile"],
                    "stars": 1500,
                    "forks": 280
                }
            ]),
            "pull_requests": json.dumps([
                {
                    "title": "Add support for custom resources",
                    "body": ("Implementing support for custom Kubernetes resources "
                             "in the operator..."),
                    "state": "merged",
                    "repository": "kubernetes/kubernetes",
                    "created_at": "2024-01-10T14:30:00Z",
                    "closed_at": "2024-01-15T16:45:00Z",
                    "merged_at": "2024-01-15T16:45:00Z",
                    "labels": ["enhancement", "k8s", "operator"],
                    "url": "https://github.com/kubernetes/kubernetes/pull/54321"
                }
            ]),
            "languages": ["Go", "Dockerfile"],
            "topics": ["kubernetes", "microservices", "cloud", "devops", "api"],
            "followers_count": 890,
            "following_count": 120,
            "total_stars_received": 1500,
            "total_forks": 280,
            "profile_text_for_embedding": (
                "Sam Rodriguez, Cloud infrastructure engineer specializing in Go and Kubernetes. "
                "Repositories: k8s-operator, Custom Kubernetes operator for managing microservices. "
                "Languages: Go, Dockerfile. "
                "Topics: kubernetes, microservices, cloud, devops."
            ),
            "last_updated": current_time.isoformat()
        },
        {
            "user_id": "d4e5f6g7-h8i9-0123-4567-890123defghi",
            "github_username": "frontend-wizard",
            "display_name": "Emily Johnson",
            "bio": "Frontend developer creating beautiful and accessible web experiences.",
            "location": "New York, NY",
            "repositories": json.dumps([
                {
                    "name": "react-components",
                    "description": "Reusable React component library with TypeScript.",
                    "url": "https://github.com/frontend-wizard/react-components",
                    "languages": ["TypeScript", "CSS", "JavaScript"],
                    "stars": 2100,
                    "forks": 420
                },
                {
                    "name": "css-animations",
                    "description": "Collection of smooth CSS animations and transitions.",
                    "url": "https://github.com/frontend-wizard/css-animations",
                    "languages": ["CSS", "HTML"],
                    "stars": 850,
                    "forks": 180
                }
            ]),
            "pull_requests": json.dumps([
                {
                    "title": "Improve accessibility features",
                    "body": ("Adding comprehensive accessibility features to the "
                             "React component library..."),
                    "state": "open",
                    "repository": "facebook/react",
                    "created_at": "2024-02-05T11:20:00Z",
                    "closed_at": None,
                    "merged_at": None,
                    "labels": ["accessibility", "enhancement", "a11y"],
                    "url": "https://github.com/facebook/react/pull/98765"
                }
            ]),
            "languages": ["TypeScript", "JavaScript", "CSS", "HTML"],
            "topics": ["react", "frontend", "typescript", "css", "ui-ux", "accessibility"],
            "followers_count": 1320,
            "following_count": 200,
            "total_stars_received": 2950,
            "total_forks": 600,
            "profile_text_for_embedding": (
                "Emily Johnson, Frontend developer creating beautiful and accessible web experiences. "
                "Repositories: react-components, Reusable React component library with TypeScript. "
                "css-animations, Collection of smooth CSS animations and transitions. "
                "Languages: TypeScript, JavaScript, CSS. "
                "Topics: react, frontend, typescript, css, ui-ux."
            ),
            "last_updated": current_time.isoformat()
        },
        {
            "user_id": "e5f6g7h8-i9j0-1234-5678-901234efghij",
            "github_username": "rust-enthusiast",
            "display_name": "David Kim",
            "bio": "Systems programmer passionate about performance and memory safety.",
            "location": "Seattle, WA",
            "repositories": json.dumps([
                {
                    "name": "memory-allocator",
                    "description": "Custom memory allocator written in Rust for high-performance applications.",
                    "url": "https://github.com/rust-enthusiast/memory-allocator",
                    "languages": ["Rust"],
                    "stars": 1750,
                    "forks": 240
                },
                {
                    "name": "concurrent-data-structures",
                    "description": "Lock-free data structures for concurrent programming in Rust.",
                    "url": "https://github.com/rust-enthusiast/concurrent-data-structures",
                    "languages": ["Rust"],
                    "stars": 1200,
                    "forks": 180
                }
            ]),
            "pull_requests": json.dumps([
                {
                    "title": "Optimize memory allocation patterns",
                    "body": ("Implementing advanced memory allocation optimization techniques "
                             "for better performance..."),
                    "state": "merged",
                    "repository": "rust-lang/rust",
                    "created_at": "2024-01-25T08:45:00Z",
                    "closed_at": "2024-02-01T10:30:00Z",
                    "merged_at": "2024-02-01T10:30:00Z",
                    "labels": ["performance", "memory", "optimization"],
                    "url": "https://github.com/rust-lang/rust/pull/13579"
                }
            ]),
            "languages": ["Rust", "C++", "Assembly"],
            "topics": ["rust", "systems-programming", "performance", "memory-safety", "concurrency"],
            "followers_count": 980,
            "following_count": 85,
            "total_stars_received": 2950,
            "total_forks": 420,
            "profile_text_for_embedding": (
                "David Kim, Systems programmer passionate about performance and memory safety. "
                "Repositories: memory-allocator, Custom memory allocator written in Rust for "
                "high-performance applications. concurrent-data-structures, Lock-free data structures "
                "for concurrent programming in Rust. Languages: Rust, C++, Assembly. "
                "Topics: rust, systems-programming, performance, memory-safety."
            ),
            "last_updated": current_time.isoformat()
        }
    ]

    try:
        collection = client.collections.get("weaviate_user_profile")
        async with collection.batch.dynamic() as batch:
            for profile in user_profiles:
                batch.add_object(
                    properties=profile
                )
        print("✅ Populated weaviate_user_profile with sample user data.")
    except Exception as e:
        print(f"❌ Error populating weaviate_user_profile: {e}")
        raise

async def populate_all_collections():
    """
    Populate only the user profile collection as per the updated model structure.
    """
    try:
        async with get_weaviate_client() as client:
            print("Populating Weaviate user profile collection with sample data...")
            await populate_weaviate_user_profile(client)
            print("✅ User profile collection populated successfully.")
    except Exception as e:
        print(f"❌ Error during population: {e}")
        raise

def main():
    """Entry point for running the population script."""
    asyncio.run(populate_all_collections())



