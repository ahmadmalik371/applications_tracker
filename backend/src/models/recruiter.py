import uuid
from datetime import datetime
from sqlalchemy import Column, String, UUID, DateTime, Integer, Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from src.models.base import Base


class Tag(Base):
    """Model for candidate tags (labels)."""
    
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    color = Column(String(20), nullable=True, default="blue")  # For UI rendering
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    organization = relationship("Organization", backref="tags")
    created_by = relationship("User", backref="created_tags")

    def __repr__(self):
        return f"<Tag {self.id}: {self.name}>"


class CandidateTag(Base):
    """Association model between candidates and tags."""
    
    __tablename__ = "candidate_tags"

    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    added_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    candidate = relationship("Candidate", backref="tags")
    tag = relationship("Tag")
    added_by = relationship("User", backref="added_tags")

    def __repr__(self):
        return f"<CandidateTag candidate={self.candidate_id} tag={self.tag_id}>"


class Note(Base):
    """Model for recruiter notes on candidates."""
    
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    content = Column(Text, nullable=False)
    is_private = Column(Boolean, default=False)  # Only visible to author if True
    
    mentions = Column(JSON, nullable=True)  # List of user IDs mentioned in note
    attachments = Column(JSON, nullable=True)  # List of attachment URLs
    
    is_deleted = Column(Boolean, default=False)  # Soft delete for audit trail
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    candidate = relationship("Candidate", backref="notes")
    author = relationship("User", backref="created_notes")

    def __repr__(self):
        return f"<Note {self.id}: candidate={self.candidate_id}>"


class NoteVersion(Base):
    """Model for tracking note edit history."""
    
    __tablename__ = "note_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=False)
    
    content = Column(Text, nullable=False)
    changed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    note = relationship("Note", backref="versions")
    changed_by = relationship("User", backref="note_changes")

    def __repr__(self):
        return f"<NoteVersion {self.id}: note={self.note_id}>"
