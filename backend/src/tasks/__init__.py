"""
Celery task modules for async processing:
- parse_resume_task: Parse uploaded resumes and extract candidate info
- generate_candidate_embedding_task: Generate vector embeddings for candidates
- generate_job_embedding_task: Generate vector embeddings for jobs
"""

from .resume_parsing import parse_resume_task
from .embeddings import generate_candidate_embedding_task, generate_job_embedding_task

__all__ = [
    "parse_resume_task",
    "generate_candidate_embedding_task",
    "generate_job_embedding_task",
]
