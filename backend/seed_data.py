"""
Seed script using the application's ORM models to create demo data.
Run with:  python seed_data.py  (uses DATABASE_URL from .env or environment)
"""
import asyncio
from datetime import datetime, timedelta

from src.core.database import AsyncSessionLocal, init_db
from src.core.security import hash_password
from src.models.auth import Role
from src.models.user import User
from src.models.organization import Organization
from src.models.job import Job, JobStatus
from src.models.candidate import Candidate
from src.models.application import Application
from src.models.recruiter import Tag, CandidateTag
from src.models.notification import Notification


async def seed():
    await init_db()

    async with AsyncSessionLocal() as db:
        hashed_pw = hash_password("password123")

        # Roles
        default_roles = [
            ("Super Admin", "Full system access"),
            ("Company Admin", "Organization administrator"),
            ("Recruiter", "Recruiter role"),
            ("Hiring Manager", "Hiring manager role"),
            ("Candidate", "Candidate role"),
        ]
        role_map = {}
        for name, desc in default_roles:
            role = Role(name=name, description=desc)
            db.add(role)
            await db.flush()
            role_map[name] = role
        await db.flush()

        # Organization
        org = Organization(name="TechCorp Inc.", is_active=True)
        db.add(org)
        await db.flush()

        # Users
        users_data = [
            ("admin@techcorp.com", "Sarah Johnson", "Company Admin"),
            ("recruiter@techcorp.com", "Mike Chen", "Recruiter"),
            ("hiring@techcorp.com", "Emily Davis", "Hiring Manager"),
        ]
        user_ids = []
        for email, name, role_name in users_data:
            user = User(
                email=email,
                hashed_password=hashed_pw,
                full_name=name,
                is_active=True,
                is_verified=True,
                role_id=role_map[role_name].id,
                organization_id=org.id,
            )
            db.add(user)
            await db.flush()
            user_ids.append(user.id)

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
            now = datetime.utcnow() - timedelta(days=days)
            job = Job(
                title=title,
                description=f"Job description for {title}",
                location=loc,
                employment_type=emp,
                status=status,
                is_published=True,
                organization_id=org.id,
                created_by_id=user_ids[0],
                created_at=now,
                updated_at=now,
            )
            db.add(job)
            await db.flush()
            job_ids.append(job.id)

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
            now = datetime.utcnow() - timedelta(days=days)
            candidate = Candidate(
                first_name=fn,
                last_name=ln,
                email=email,
                status=status,
                organization_id=org.id,
                created_at=now,
                updated_at=now,
            )
            db.add(candidate)
            await db.flush()
            candidate_ids.append(candidate.id)

        # Tags
        all_skills = set()
        for _, _, _, _, _, skills in candidates_data:
            for s in skills:
                all_skills.add(s)
        tag_map = {}
        now = datetime.utcnow()
        for skill in all_skills:
            tag = Tag(
                name=skill,
                organization_id=org.id,
                created_at=now,
                updated_at=now,
            )
            db.add(tag)
            await db.flush()
            tag_map[skill] = tag

        # Candidate Tags
        for (fn, ln, email, status, days, skills), cid in zip(candidates_data, candidate_ids):
            for skill in skills:
                ct = CandidateTag(
                    candidate_id=cid,
                    tag_id=tag_map[skill].id,
                    created_at=now,
                )
                db.add(ct)

        # Applications
        for i, (fn, ln, email, status, days, skills) in enumerate(candidates_data):
            stage = status if status != "New" else "Applied"
            jid = job_ids[i % len(job_ids)]
            cid = candidate_ids[i]
            now = datetime.utcnow() - timedelta(days=days)
            score = round(60 + (hash(email) % 40), 1)
            app = Application(
                candidate_id=cid,
                job_id=jid,
                organization_id=org.id,
                status=stage,
                score=score,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            db.add(app)

        # Notifications for the admin user
        notif_data = [
            ("New Application", f"{candidates_data[0][0]} {candidates_data[0][1]} applied for Senior Python Developer", False, 1),
            ("Candidate Shortlisted", f"{candidates_data[5][0]} {candidates_data[5][1]} has been moved to Offer stage", False, 3),
            ("Interview Scheduled", f"Interview with {candidates_data[2][0]} {candidates_data[2][1]} is scheduled for tomorrow", False, 5),
            ("New Job Posted", "Senior Python Developer job has been published", True, 2),
            ("Candidate Hired", f"{candidates_data[6][0]} {candidates_data[6][1]} has accepted the offer", True, 7),
        ]
        for title, message, read, days in notif_data:
            now = datetime.utcnow() - timedelta(days=days)
            notif = Notification(
                organization_id=org.id,
                user_id=user_ids[0],
                channel="in_app",
                title=title,
                message=message,
                status="sent",
                read=read,
                created_at=now,
            )
            db.add(notif)

        await db.commit()
        print("Seed data created successfully!")
        print(f"   Organization: TechCorp Inc.")
        print(f"   Users: 3 (admin@techcorp.com, recruiter@techcorp.com, hiring@techcorp.com)")
        print(f"   Jobs: {len(jobs_data)}")
        print(f"   Candidates: {len(candidates_data)}")
        print(f"   Tags: {len(tag_map)}")
        print(f"   Applications: {len(candidates_data)}")
        print()
        print("Login credentials for all users: password123")


asyncio.run(seed())
