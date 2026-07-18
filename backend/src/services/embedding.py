import json
from typing import Optional, List
import hashlib

# Mock embedding function for demonstration
# In production, this would integrate with OpenAI, Hugging Face, etc.


def generate_mock_embedding(text: str, dimension: int = 1536) -> List[float]:
    """
    Generate a mock embedding for testing.
    In production, replace with actual embedding service (OpenAI, HuggingFace, etc.).
    """
    # Create a deterministic hash-based embedding
    hash_obj = hashlib.sha256(text.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Convert hash to embedding by using it as seed for pseudo-random values
    embedding = []
    for i in range(dimension):
        # Use hash + index to generate consistent pseudo-random values
        chunk = hash_hex[(i * 2) % len(hash_hex):(i * 2 + 2) % len(hash_hex)]
        if chunk:
            value = (int(chunk, 16) / 255.0) * 2.0 - 1.0  # Normalize to [-1, 1]
        else:
            value = 0.0
        embedding.append(value)
    
    return embedding


async def generate_candidate_embedding(parsed_resume_data: dict) -> List[float]:
    """
    Generate embedding for candidate based on parsed resume data.
    """
    try:
        # Extract key information for embedding
        contact_info = parsed_resume_data.get('contact_info', {})
        skills = parsed_resume_data.get('skills', [])
        experience_level = parsed_resume_data.get('experience_level', '')
        summary = parsed_resume_data.get('summary', '')
        
        # Combine into a text representation
        embedding_text = f"""
        Skills: {', '.join(skills)}
        Experience: {experience_level}
        Summary: {summary}
        """
        
        # Generate embedding
        embedding = generate_mock_embedding(embedding_text)
        return embedding
    except Exception as e:
        raise ValueError(f"Failed to generate candidate embedding: {str(e)}")


async def generate_job_embedding(job_description: str) -> List[float]:
    """
    Generate embedding for job based on job description.
    """
    try:
        # Generate embedding from job description
        embedding = generate_mock_embedding(job_description)
        return embedding
    except Exception as e:
        raise ValueError(f"Failed to generate job embedding: {str(e)}")


async def compute_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Compute cosine similarity between two embeddings.
    """
    if not embedding1 or not embedding2:
        return 0.0
    
    if len(embedding1) != len(embedding2):
        return 0.0
    
    # Compute dot product
    dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
    
    # Compute magnitudes
    mag1 = sum(a ** 2 for a in embedding1) ** 0.5
    mag2 = sum(b ** 2 for b in embedding2) ** 0.5
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    # Compute cosine similarity
    similarity = dot_product / (mag1 * mag2)
    
    return similarity
