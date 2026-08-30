import hashlib
import uuid
from app.core.config import Settings
from app.core.logging import get_logger
from app.models.resume_file import ResumeFile

logger = get_logger(__name__)


class StorageService:
    """
    Manages Supabase Storage pre-signed upload URLs and physical file records.
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    def generate_upload_metadata(
        self,
        *,
        user_id: uuid.UUID,
        filename: str,
        mime_type: str,
        file_size_bytes: int,
        file_bytes: bytes | None = None,
    ) -> tuple[str, str, str]:
        """
        Generates a secure storage path, dummy/signed upload URL, and checksum.
        Storage path format: resumes/{user_id}/{file_uuid}.{ext}
        """
        file_uuid = uuid.uuid4()
        ext = "pdf" if "pdf" in mime_type or filename.lower().endswith(".pdf") else "docx"
        storage_path = f"resumes/{user_id}/{file_uuid}.{ext}"

        # Calculate or approximate SHA-256 checksum
        if file_bytes:
            checksum = hashlib.sha256(file_bytes).hexdigest()
        else:
            checksum = hashlib.sha256(f"{user_id}_{filename}_{file_uuid}".encode()).hexdigest()

        # In full Supabase deployment, use supabase client create_signed_upload_url
        # For direct API upload or local testing, provide upload endpoint path
        upload_url = f"/api/v1/storage/upload/{storage_path}"

        return storage_path, upload_url, checksum
