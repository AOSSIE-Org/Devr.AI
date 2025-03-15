from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import requests
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from supabase import create_client
import openai

# Load environment variables
load_dotenv()

# Initialize embeddings model
try:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
except Exception as e:
    print(f"Error loading embeddings: {e}")
    exit(1)

# Supabase setup
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    print("🚨 Supabase credentials are missing! Check your .env file.")
    exit(1)

supabase = create_client(supabase_url, supabase_key)

# Groq API setup
openai.api_key = os.getenv('GROQ_API_KEY')


# GitHub API to fetch contributors
def fetch_github_contributors(repo_owner, repo_name):
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("🚨 GITHUB_TOKEN is missing! Set it in .env file.")
        return []

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contributors"
    headers = {'Authorization': f'token {github_token}', 'Accept': 'application/vnd.github.v3+json'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"⚠️ Failed to fetch contributors: {response.status_code} - {response.text}")
        print(f"🔍 Check if the repo exists: {url}")
        return []


# Store contributor data in Supabase
def store_contributor_data(contributors):
    if not contributors:
        print("No contributors found.")
        return
    for contributor in contributors:
        data = {"username": contributor['login'], "contributions": contributor['contributions']}
        supabase.table('contributors').insert(data).execute()


# Prepare documents for vector store
def prepare_documents(contributors):
    documents = []
    for contributor in contributors:
        name = contributor['login']
        tags = [f"#{name}", "#contributor"]
        documents.append(Document(page_content=" ".join(tags), metadata={"reviewer": name}))
    return documents


# Store contributor data in FAISS
def create_vector_store(documents):
    if not documents:
        print("⚠️ Error: No documents to create vector store!")
        return None
    return FAISS.from_documents(documents, embeddings)


# Store PR details in Supabase
def store_pr_data(pr_title, pr_body, pr_link, reviewer):
    data = {"pr_title": pr_title, "pr_body": pr_body, "pr_link": pr_link, "reviewer": reviewer}
    supabase.table('pull_requests').insert(data).execute()


# Get PR insights using Groq LLM
def get_pr_insights(pr_title, pr_body):
    prompt = f"Analyze the following PR details and suggest keywords: Title: {pr_title}, Body: {pr_body}"
    try:
        response = openai.Completion.create(
            engine="gpt-4",
            prompt=prompt,
            max_tokens=100
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error using Groq API: {e}")
        return ""


# Assign PR to top reviewers using FAISS and Groq insights
def assign_reviewers(pr_title, pr_body, pr_link, vector_store):
    if not vector_store:
        print("⚠️ Error: Vector store is not initialized.")
        return

    pr_content = pr_title + " " + pr_body
    pr_embedding = embeddings.embed_query(pr_content)
    groq_insights = get_pr_insights(pr_title, pr_body)

    results = vector_store.similarity_search_by_vector(pr_embedding, k=2)

    print("🔹 Top 2 Reviewers based on FAISS and Groq:")
    for result in results:
        reviewer = result.metadata['reviewer']
        print(f"✅ Assigned Reviewer: {reviewer} | Groq Insights: {groq_insights}")
        store_pr_data(pr_title, pr_body, pr_link, reviewer)
        notify_discord(reviewer, pr_link)
        notify_github(pr_link, reviewer)


# Notify Discord
def notify_discord(reviewer, pr_link):
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        print("⚠️ Discord Webhook URL is missing.")
        return
    payload = {"content": f"Hey {reviewer}, a new PR needs your review: {pr_link}"}
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code != 204:
            print(f"⚠️ Failed to notify Discord: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error notifying Discord: {e}")


# Notify GitHub with a comment
def notify_github(pr_link, reviewer):
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("🚨 GitHub Token is missing! Set it in .env file.")
        return

    api_url = pr_link.replace("https://github.com/", "https://api.github.com/repos/").replace("/pull/",
                                                                                              "/issues/") + "/comments"
    payload = {"body": f"@{reviewer} has been assigned to review this PR."}
    headers = {'Authorization': f'token {github_token}', 'Accept': 'application/vnd.github.v3+json'}

    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code != 201:
        print(f"⚠️ Failed to add GitHub comment: {response.status_code} - {response.text}")


# Flask app to listen for GitHub events
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data.get('action') == 'opened' and 'pull_request' in data:
        pr_title = data['pull_request']['title']
        pr_body = data['pull_request']['body']
        pr_link = data['pull_request']['html_url']
        assign_reviewers(pr_title, pr_body, pr_link, vector_store)
    return jsonify({"status": "ok"}), 200


# Main execution
repo_owner = "example"
repo_name = "repo"
contributors = fetch_github_contributors(repo_owner, repo_name)

if contributors:
    store_contributor_data(contributors)
    documents = prepare_documents(contributors)
    vector_store = create_vector_store(documents)
    print("✅ Vector store successfully created.")
else:
    print("⚠️ Skipping vector store creation due to missing contributors.")
    vector_store = None

if __name__ == '__main__':
    app.run(port=5000)
