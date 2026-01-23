"""Storage API endpoints for upload, download, delete, and list files with authentication."""

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from db.session import get_session
from api.dependencies import get_current_user, get_storage_service
from services.storage import StorageService
from repositories.file import FileRepository
from schemas.storage import (
    FileUploadRequest,
    FileUploadResponse,
    FileInfo,
    FileListResponse,
    FileDeleteResponse,
    SuccessResponse,
)
from core.exceptions import NotFoundError, ValidationError
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/storage",
    tags=["storage"]
)


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    bucket_type: str = "documents",
    make_public: bool = False,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service),
):
    """
    Upload a file to Supabase Storage.
    
    Args:
        file: Uploaded file
        bucket_type: Type of bucket (images, documents, artifacts)
        make_public: Whether to make the file publicly accessible
        db: Database session
        current_user: Authenticated user
        storage_service: Storage service instance
        
    Returns:
        File upload response with metadata
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Upload to storage
        upload_result = storage_service.upload_file(
            file_content=file_content,
            filename=file.filename or "unnamed",
            bucket_type=bucket_type,
            user_id=current_user.get("id"),
            content_type=file.content_type,
            make_public=make_public,
        )
        
        # Save file metadata to database
        file_repo = FileRepository()
        file_model = file_repo.create(db, {
            "filename": upload_result["filename"],
            "storage_path": upload_result["storage_path"],
            "size": upload_result["size"],
            "content_type": upload_result["content_type"],
            "file_hash": upload_result["file_hash"],
            "bucket_name": upload_result["bucket_name"],
            "bucket_type": upload_result["bucket_type"],
            "uploaded_by": current_user.get("id"),
            "is_public": upload_result["is_public"],
            "file_metadata": upload_result.get("metadata"),
        })
        
        return FileUploadResponse(
            message="File uploaded successfully",
            data={
                "id": file_model.id,
                **upload_result
            }
        )
        
    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/download/{file_id}")
async def download_file(
    file_id: int,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service),
):
    """
    Download a file from Supabase Storage.
    
    Args:
        file_id: File ID
        db: Database session
        current_user: Authenticated user
        storage_service: Storage service instance
        
    Returns:
        File content as streaming response
    """
    file_repo = FileRepository()
    file_model = file_repo.get(db, file_id)
    
    if not file_model:
        raise NotFoundError("File", str(file_id))
    
    # Check access permissions
    if not file_model.is_public and file_model.uploaded_by != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this file"
        )
    
    try:
        # Download from storage
        file_content = storage_service.download_file(
            file_model.storage_path,
            file_model.bucket_name
        )
        
        return Response(
            content=file_content,
            media_type=file_model.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{file_model.filename}"'
            }
        )
        
    except Exception as e:
        logger.error(f"File download failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File download failed: {str(e)}"
        )


@router.delete("/{file_id}", response_model=FileDeleteResponse)
async def delete_file(
    file_id: int,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service),
):
    """
    Delete a file from Supabase Storage.
    
    Args:
        file_id: File ID
        db: Database session
        current_user: Authenticated user
        storage_service: Storage service instance
        
    Returns:
        Deletion confirmation
    """
    file_repo = FileRepository()
    file_model = file_repo.get(db, file_id)
    
    if not file_model:
        raise NotFoundError("File", str(file_id))
    
    # Check permissions (only owner can delete)
    if file_model.uploaded_by != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this file"
        )
    
    try:
        # Delete from storage
        storage_service.delete_file(
            file_model.storage_path,
            file_model.bucket_name
        )
        
        # Delete from database
        file_repo.delete(db, file_id)
        
        return FileDeleteResponse(
            message="File deleted successfully",
            data={
                "storage_path": file_model.storage_path,
                "deleted": True
            }
        )
        
    except Exception as e:
        logger.error(f"File deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File deletion failed: {str(e)}"
        )


@router.get("/list", response_model=FileListResponse)
async def list_files(
    bucket_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    List files with optional filtering.
    
    Args:
        bucket_type: Optional bucket type filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Paginated list of files
    """
    file_repo = FileRepository()
    
    # Get user's files or public files
    if bucket_type:
        files = file_repo.get_by_bucket(db, bucket_type, skip=skip, limit=limit)
    else:
        files = file_repo.get_by_user(
            db,
            current_user.get("id"),
            skip=skip,
            limit=limit
        )
    
    # Convert to response format
    file_infos = []
    for file_model in files:
        file_info = FileInfo(
            id=file_model.id,
            filename=file_model.filename,
            storage_path=file_model.storage_path,
            size=file_model.size,
            content_type=file_model.content_type,
            bucket_name=file_model.bucket_name,
            bucket_type=file_model.bucket_type,
            is_public=file_model.is_public,
            uploaded_by=file_model.uploaded_by,
            created_at=file_model.created_at.isoformat(),
        )
        file_infos.append(file_info)
    
    total = file_repo.count(db, {"uploaded_by": current_user.get("id")} if not bucket_type else {"bucket_type": bucket_type})
    total_pages = (total + limit - 1) // limit
    
    return FileListResponse(
        message="Files retrieved successfully",
        data=file_infos,
        page=(skip // limit) + 1,
        page_size=limit,
        total=total,
        total_pages=total_pages,
        has_next=(skip + limit) < total,
        has_previous=skip > 0,
    )


@router.get("/{file_id}/url")
async def get_file_url(
    file_id: int,
    expires_in: int = 3600,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service),
):
    """
    Get a signed URL for a file (temporary access).
    
    Args:
        file_id: File ID
        expires_in: Expiration time in seconds (default: 1 hour)
        db: Database session
        current_user: Authenticated user
        storage_service: Storage service instance
        
    Returns:
        Signed URL
    """
    file_repo = FileRepository()
    file_model = file_repo.get(db, file_id)
    
    if not file_model:
        raise NotFoundError("File", str(file_id))
    
    # Check access permissions
    if not file_model.is_public and file_model.uploaded_by != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this file"
        )
    
    try:
        if file_model.is_public:
            url = storage_service.get_public_url(
                file_model.storage_path,
                file_model.bucket_name
            )
        else:
            url = storage_service.get_signed_url(
                file_model.storage_path,
                file_model.bucket_name,
                expires_in=expires_in
            )
        
        return SuccessResponse(
            message="URL generated successfully",
            data={
                "url": url,
                "expires_in": expires_in if not file_model.is_public else None,
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to generate URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate URL: {str(e)}"
        )

