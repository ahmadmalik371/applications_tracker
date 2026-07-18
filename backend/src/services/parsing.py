import os
import re
import uuid
from typing import Optional, Dict, Any
from pathlib import Path
from pypdf import PdfReader

from src.core.config import get_settings

settings = get_settings()


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file (simple implementation)."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except ImportError:
        # Fallback if python-docx not installed
        return ""
    except Exception as e:
        raise ValueError(f"Failed to extract text from DOCX: {str(e)}")


def extract_text_from_file(file_path: str) -> str:
    """Extract text from resume file based on file type."""
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_ext in ['.doc', '.docx']:
        return extract_text_from_docx(file_path)
    elif file_ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")


def parse_contact_info(text: str) -> Dict[str, Optional[str]]:
    """Extract contact information from resume text."""
    # Simple regex patterns for contact info
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'(?:\+?1[-.\s]?)?\(?(?:\d{3})\)?[-.\s]?(?:\d{3})[-.\s]?(?:\d{4})'
    
    email_match = re.search(email_pattern, text)
    phone_match = re.search(phone_pattern, text)
    
    return {
        'email': email_match.group(0) if email_match else None,
        'phone': phone_match.group(0) if phone_match else None,
    }


def extract_skills(text: str) -> list[str]:
    """Extract likely skills from resume text."""
    # Common technical skills
    technical_skills = {
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'golang', 'rust',
        'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis',
        'react', 'vue', 'angular', 'node.js', 'django', 'flask', 'fastapi',
        'aws', 'gcp', 'azure', 'kubernetes', 'docker',
        'machine learning', 'deep learning', 'nlp', 'computer vision',
        'data science', 'data engineering', 'analytics',
    }
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in technical_skills:
        if skill in text_lower:
            found_skills.append(skill)
    
    return found_skills


def extract_years_of_experience(experience: list) -> int:
    """Extract total years of experience from a list of experience entries.

    Accepts either structured dicts (with a ``duration`` key) or plain strings.
    Returns 0 when no duration can be parsed.
    """
    if not experience:
        return 0

    total = 0
    pattern = re.compile(r"(\d+)\s*(?:\+)?\s*(?:years?|yrs?)", re.IGNORECASE)

    for entry in experience:
        if isinstance(entry, dict):
            duration = str(entry.get("duration", "")) + " " + str(entry.get("title", ""))
        else:
            duration = str(entry)

        matches = pattern.findall(duration)
        for value in matches:
            total += int(value)

    return total


def extract_experience_level(text: str) -> str:
    """Estimate experience level from resume text."""
    text_lower = text.lower()
    
    # Look for years of experience
    years_pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)'
    years_match = re.search(years_pattern, text_lower)
    
    if years_match:
        years = int(years_match.group(1))
        if years < 2:
            return "Entry Level"
        elif years < 5:
            return "Mid Level"
        elif years < 10:
            return "Senior"
        else:
            return "Lead/Principal"
    
    return "Unknown"


def parse_resume_text(text: str) -> Dict[str, Any]:
    """Parse resume text and extract structured data."""
    try:
        contact_info = parse_contact_info(text)
        skills = extract_skills(text)
        experience_level = extract_experience_level(text)
        
        # Summarize text (first 500 chars)
        summary = text[:500].strip()
        
        return {
            'contact_info': contact_info,
            'skills': skills,
            'experience_level': experience_level,
            'summary': summary,
            'raw_text': text,
        }
    except Exception as e:
        raise ValueError(f"Failed to parse resume: {str(e)}")


async def parse_resume_from_file(resume_url: str) -> Dict[str, Any]:
    """
    Main function to parse resume from file URL.
    Extracts text and structured data.
    """
    # Convert URL to file path
    file_path = resume_url.replace("/uploads/", settings.UPLOADS_DIR + "/")
    
    if not os.path.exists(file_path):
        raise ValueError(f"Resume file not found: {file_path}")
    
    # Extract text from file
    text = extract_text_from_file(file_path)
    
    # Parse structured data
    parsed_data = parse_resume_text(text)
    
    return parsed_data
