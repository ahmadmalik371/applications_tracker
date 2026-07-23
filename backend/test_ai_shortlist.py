import asyncio
import httpx
import uuid

API_BASE = "http://localhost:8000/api/v1"

# Sample Candidate Resumes
CANDIDATES = [
    {
        "first_name": "Alice",
        "last_name": "Senior-Python-Dev",
        "email": "alice.dev@example.com",
        "resume_content": """
Alice Smith
Senior Python & AI Engineer with 8 years of experience.
Skills: Python, FastAPI, PostgreSQL, SQLAlchemy, Celery, Redis, Machine Learning, Docker, Next.js.
Experience:
- Senior Backend Engineer at TechCorp: Built scalable REST APIs using FastAPI & SQLAlchemy. Integrated Celery background tasks for heavy AI model processing.
- Software Engineer at DataInc: Designed PostgreSQL databases, optimized queries, used Redis caching.
Education: M.S. in Computer Science.
"""
    },
    {
        "first_name": "Bob",
        "last_name": "Frontend-React-Dev",
        "email": "bob.react@example.com",
        "resume_content": """
Bob Jones
Frontend Developer specializing in React and HTML/CSS.
Skills: React, JavaScript, HTML, CSS, TailwindCSS, Figma.
Experience:
- UI Developer at WebStudio: Designed responsive UI pages with HTML & CSS.
Education: B.S. in Graphic Design.
"""
    },
    {
        "first_name": "Charlie",
        "last_name": "Junior-Generalist",
        "email": "charlie.jr@example.com",
        "resume_content": """
Charlie Brown
Junior Developer with basic knowledge of Python and JavaScript.
Skills: Python, JavaScript, Git.
Experience: Internship at Local Agency editing WordPress sites and basic Python scripts.
Education: Bootcamp Certificate.
"""
    }
]

JOB_TITLE = "Senior Python AI Engineer"
JOB_DESC = """
We are seeking a Senior Python AI Engineer with deep experience in FastAPI, SQLAlchemy, PostgreSQL, Celery, Redis, and Machine Learning workflows.
Requirements:
- 5+ years of Python experience
- Hands-on FastAPI, PostgreSQL, SQLAlchemy, Redis, Celery
- Experience with AI embedding generation, vector search, and model scoring
"""

async def test_end_to_end():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("1. Logging in as Admin...")
        login_res = await client.post(f"{API_BASE}/auth/login", data={"username": "admin@example.com", "password": "AdminPassword123!"})
        test_email = f"admin_{uuid.uuid4().hex[:6]}@example.com"
        print(f"Signing up as new admin ({test_email})...")
        signup_res = await client.post(f"{API_BASE}/auth/register", json={
            "email": test_email,
            "password": "AdminPassword123!",
            "full_name": "Test Admin",
            "organization_name": "Test Organization"
        })
        token = signup_res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print("-> Authenticated successfully as Company Admin.")

        print("\n2. Creating test Job Opening:", JOB_TITLE)
        job_res = await client.post(f"{API_BASE}/jobs", headers=headers, json={
            "title": JOB_TITLE,
            "description": JOB_DESC,
            "department": "Engineering",
            "location": "Remote",
            "employment_type": "Full-time",
            "salary_range": "$140,000 - $180,000"
        })
        job = job_res.json()
        if job_res.status_code != 201:
            print("Job creation response failed:", job_res.status_code, job)
            return
        job_id = job["id"]
        print(f"-> Job Created with ID: {job_id}")

        print("\n3. Uploading & Submitting 3 Resumes for Job Application...")
        applications = []
        for cdata in CANDIDATES:
            # Create candidate & application via public_jobs endpoints or internal endpoints
            files = {"file": (f"{cdata['first_name']}_resume.txt", cdata["resume_content"].encode("utf-8"), "text/plain")}
            data = {
                "first_name": cdata["first_name"],
                "last_name": cdata["last_name"],
                "email": cdata["email"],
                "job_id": job_id
            }
            app_res = await client.post(f"{API_BASE}/public/jobs/{job_id}/apply", data=data, files=files)
            if app_res.status_code == 201:
                app = app_res.json()
                applications.append((cdata['first_name'], app))
                print(f"-> Applied: {cdata['first_name']} {cdata['last_name']} (App ID: {app['id']})")
            else:
                print(f"FAILED application for {cdata['first_name']}:", app_res.status_code, app_res.text)

        print("\n4. Waiting 5 seconds for Celery Workers to parse, embed, score and generate AI explanations...")
        await asyncio.sleep(5)

        print("\n5. Fetching Rankings & Shortlist Results for the Job:")
        rank_res = await client.get(f"{API_BASE}/rankings/candidates/for-job/{job_id}", headers=headers)
        if rank_res.status_code == 200:
            rankings = rank_res.json()
            print("\n=================== AI SHORTLIST RANKINGS ===================")
            for idx, item in enumerate(rankings, 1):
                print(f"Rank #{idx}: {item['candidate_name']} ({item['candidate_email']})")
                print(f"   Match Score: {round(item['match_score'] * 100, 1)}% | Confidence: {round(item['confidence'] * 100, 1)}%")
                print(f"   Embedding Sim: {round(item.get('embedding_similarity', 0) * 100, 1)}%")
                print("-" * 60)
        else:
            print("Failed to fetch rankings:", rank_res.status_code, rank_res.text)

if __name__ == "__main__":
    asyncio.run(test_end_to_end())
