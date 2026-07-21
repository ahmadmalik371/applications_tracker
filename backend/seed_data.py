"""
Seed script using the application's own services to create demo data.
Run with:  docker exec -i ats-backend-1 python seed_data.py
"""
import os
os.environ["DATABASE_URL"] = "postgresql+asyncpg://ats_user:13851098@db:5432/ats_db"

import sys
import uuid
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import text
from src.core.database import AsyncSessionLocal
from src.core.security import hash_password

async def seed():
    async with AsyncSessionLocal() as db:
        # Use argon2 hashing via application's security module
        hashed_pw = hash_password("password123")

        # Get existing roles
        result = await db.execute(text("SELECT id, name FROM roles"))
        role_rows = result.fetchall()
        roles = {r[1]: r[0] for r in role_rows}

        # Organization
        org_id = uuid.uuid4()
        await db.execute(
            text("INSERT INTO organizations (id, name, is_active) VALUES (:id, :name, :active)"),
            {"id": org_id, "name": "TechCorp Inc.", "active": True}
        )

        # Users
        user_ids = []
        users_data = [
            ("admin@techcorp.com", "Sarah Johnson", "Company Admin"),
            ("recruiter@techcorp.com", "Mike Chen", "Recruiter"),
            ("hiring@techcorp.com", "Emily Davis", "Hiring Manager"),
        ]
        for email, name, role_name in users_data:
            uid = uuid.uuid4()
            now = datetime.utcnow()
            await db.execute(
                text("INSERT INTO users (id, email, hashed_password, full_name, is_active, is_verified, role_id, organization_id, created_at, updated_at) VALUES (:id, :email, :pw, :name, true, true, :rid, :oid, :now, :now)"),
                {"id": uid, "email": email, "pw": hashed_pw, "name": name, "rid": roles[role_name], "oid": org_id, "now": now}
            )
            user_ids.append(uid)

        # Jobs
        jobs_data = [
            ("Senior Python Developer", "San Francisco, CA", "Full-time", "Open", 2),
            ("Frontend Engineer (React)", "Remote", "Full-time", "Open", 5),
            ("DevOps Engineer", "New York, NY", "Full-time", "Open", 7),
            ("Product Designer", "San Francisco, CA", "Full-time", "Open", 10),
            ("Data Scientist", "Remote", "Contract", "Open", 3),
            ("Junior QA Engineer", "Austin, TX", "Full-time", "Closed", 30),
        ]
        job_ids = []
        for title, loc, emp, status, days in jobs_data:
            jid = uuid.uuid4()
            now = datetime.utcnow() - timedelta(days=days)
            await db.execute(
                text("""INSERT INTO jobs (id, title, description, location, employment_type, status, is_published, organization_id, created_by_id, created_at, updated_at) 
                         VALUES (:id, :title, :desc, :loc, :emp, :status, true, :oid, :uid, :now, :now)"""),
                {"id": jid, "title": title, "desc": f"Job description for {title}", "loc": loc, "emp": emp, "status": status, "oid": org_id, "uid": user_ids[0], "now": now}
            )
            job_ids.append(jid)

        # Candidates
        candidates_data = [
            ("Alice", "Wang", "alice.wang@email.com", "New", 1, ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"]),
            ("Bob", "Smith", "bob.smith@email.com", "Screening", 3, ["React", "TypeScript", "Next.js", "Tailwind CSS"]),
            ("Carol", "Martinez", "carol.m@email.com", "Interview", 5, ["Kubernetes", "Terraform", "AWS", "CI/CD", "Prometheus"]),
            ("David", "Kim", "david.kim@email.com", "New", 0, ["Figma", "UI/UX", "Design Systems", "Prototyping"]),
            ("Eve", "Johnson", "eve.j@email.com", "Applied", 2, ["Python", "TensorFlow", "NLP", "SQL", "PyTorch"]),
            ("Frank", "Brown", "frank.brown@email.com", "Offer", 7, ["Python", "Django", "React", "PostgreSQL"]),
            ("Grace", "Lee", "grace.lee@email.com", "Hired", 14, ["Java", "Spring Boot", "Microservices", "Docker"]),
            ("Henry", "Wilson", "henry.w@email.com", "Rejected", 10, ["Python", "Flask", "MongoDB"]),
        ]
        candidate_ids = []
        for fn, ln, email, status, days, skills in candidates_data:
            cid = uuid.uuid4()
            now = datetime.utcnow() - timedelta(days=days)
            await db.execute(
                text("INSERT INTO candidates (id, first_name, last_name, email, status, organization_id, created_at, updated_at) VALUES (:id, :fn, :ln, :email, :status, :oid, :now, :now)"),
                {"id": cid, "fn": fn, "ln": ln, "email": email, "status": status, "oid": org_id, "now": now}
            )
            candidate_ids.append(cid)

        # Tags
        all_skills = set()
        for _, _, _, _, _, skills in candidates_data:
            for s in skills:
                all_skills.add(s)
        tag_map = {}
        for skill in all_skills:
            tid = uuid.uuid4()
            await db.execute(
                text("INSERT INTO tags (id, name, organization_id) VALUES (:id, :name, :oid)"),
                {"id": tid, "name": skill, "oid": org_id}
            )
            tag_map[skill] = tid

        # Candidate Tags
        for (fn, ln, email, status, days, skills), cid in zip(candidates_data, candidate_ids):
            for skill in skills:
                await db.execute(
                    text("INSERT INTO candidate_tags (candidate_id, tag_id) VALUES (:cid, :tid)"),
                    {"cid": cid, "tid": tag_map[skill]}
                )

        # Applications
        for i, (fn, ln, email, status, days, skills) in enumerate(candidates_data):
            stage = status if status != "New" else "Applied"
            jid = job_ids[i % len(job_ids)]
            cid = candidate_ids[i]
            now = datetime.utcnow() - timedelta(days=days)
            score = round(60 + (hash(email) % 40), 1)
            await db.execute(
                text("INSERT INTO applications (id, candidate_id, job_id, organization_id, status, score, created_at, updated_at) VALUES (:id, :cid, :jid, :oid, :status, :score, :now, :now)"),
                {"id": uuid.uuid4(), "cid": cid, "jid": jid, "oid": org_id, "status": stage, "score": score, "now": now}
            )

        await db.commit()
        print("✅ Seed data created successfully!")
        print(f"   Organization: TechCorp Inc.")
        print(f"   Users: 3 (admin@techcorp.com, recruiter@techcorp.com, hiring@techcorp.com)")
        print(f"   Jobs: {len(jobs_data)}")
        print(f"   Candidates: {len(candidates_data)}")
        print(f"   Tags: {len(tag_map)}")
        print(f"   Applications: {len(candidates_data)}")
        print()
        print("Login credentials for all users: password123")

asyncio.run(seed())