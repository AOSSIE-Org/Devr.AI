# Setting Up the .env File for FastAPI

This guide provides step-by-step instructions to configure your `.env` file and securely use a GitHub Personal Access Token in your FastAPI project.

## 1. Create the `.env` File

1. Navigate to the `backend` directory where your project is set up.
2. Create a new file named `.env` (if it doesn’t already exist).

## 2. Add the GitHub Access Token

1. Open the `.env` file and add the following line:
   
   ```text
   GITHUB_TOKEN=your_personal_access_token_here
   ```
   
2. Replace `your_personal_access_token_here` with your actual GitHub Personal Access Token.

## 3. Generate a GitHub Personal Access Token

1. Go to [GitHub Developer Settings](https://github.com/settings/tokens).
2. Click on  **Tokens (classic)** and then **Generate new token** and then generate the classic token.
3. Select the required scopes for your application:
   - **For public repositories**: Check `repo`.
   - **For additional access**: Check `read:org`, `read:user`, etc., as needed.
4. Copy the generated token (it will only be displayed once).


## 5. Load Environment Variables in FastAPI

Ensure you have these things installed in your project:

```bash
pip install python-dotenv requests fastapi uvicorn

```

### Test API Requests
Run your FastAPI server:

```bash
uvicorn backend.main:app --reload
```

Use `curl` or **Postman** to test the `/api/repo-stats` endpoint:

```bash
curl -X POST http://localhost:8000/api/repo-stats \
     -H "Content-Type: application/json" \
     -d '{"repo_url": "https://github.com/AOSSIE-Org/Devr.AI/"}'
```

If all the things correctly got setup then you will see the JSON repsponse

---


Now, your FastAPI application is securely set up to use GitHub API credentials from a `.env` file!