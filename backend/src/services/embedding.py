import hashlib

# Mock embedding function for demonstration
# In production, this would integrate with OpenAI, Hugging Face, etc.


def generate_mock_embedding(text: str, dimension: int = 1536) -> list[float]:
    """
    Generate a deterministic mock embedding for testing.
    In production, replace with actual embedding service (OpenAI, HuggingFace, etc.).
    """
    embedding: list[float] = []
    for i in range(dimension):
        # Hash text + index together so every dimension gets a unique 2-hex chunk
        chunk_hash = hashlib.sha256(f"{text}:{i}".encode()).hexdigest()
        value = (int(chunk_hash[:2], 16) / 255.0) * 2.0 - 1.0  # Normalize to [-1, 1]
        embedding.append(value)
    return embedding


async def generate_candidate_embedding(parsed_resume_data: dict) -> list[float]:
    """
    Generate embedding for candidate based on parsed resume data.
    """
    try:
        # Extract key information for embedding
        contact_info = parsed_resume_data.get("contact_info", {})
        skills = parsed_resume_data.get("skills", [])
        experience_level = parsed_resume_data.get("experience_level", "")
        summary = parsed_resume_data.get("summary", "")

        # Combine into a text representation
        embedding_text = f"""
        Skills: {", ".join(skills)}
        Experience: {experience_level}
        Summary: {summary}
        """

        # Generate embedding
        embedding = generate_mock_embedding(embedding_text)
        return embedding
    except Exception as e:
        raise ValueError(f"Failed to generate candidate embedding: {str(e)}")


async def generate_job_embedding(job_description: str) -> list[float]:
    """
    Generate embedding for job based on job description.
    """
    try:
        # Generate embedding from job description
        embedding = generate_mock_embedding(job_description)
        return embedding
    except Exception as e:
        raise ValueError(f"Failed to generate job embedding: {str(e)}")


async def compute_similarity(embedding1: list[float], embedding2: list[float]) -> float:
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
    mag1 = sum(a**2 for a in embedding1) ** 0.5
    mag2 = sum(b**2 for b in embedding2) ** 0.5

    if mag1 == 0 or mag2 == 0:
        return 0.0

    # Compute cosine similarity
    similarity = dot_product / (mag1 * mag2)

    return similarity


class EmbeddingService:
    """Service wrapper for generating and comparing embeddings."""

    async def generate_candidate_embedding(
        self, parsed_resume_data: dict
    ) -> list[float]:
        return await generate_candidate_embedding(parsed_resume_data)

    async def generate_job_embedding(self, job_description: str) -> list[float]:
        return await generate_job_embedding(job_description)

    async def compute_similarity(
        self, embedding1: list[float], embedding2: list[float]
    ) -> float:
        return compute_similarity(embedding1, embedding2)
