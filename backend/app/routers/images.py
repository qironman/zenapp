# Image upload router for ZenApp

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
import uuid
from PIL import Image
import io

from ..auth import get_current_user

router = APIRouter(prefix="/api/books", tags=["images"])

# Constants
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGE_WIDTH = 1200
IMAGE_QUALITY = 85
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.heic', '.webp'}

def get_images_dir(book_slug: str) -> Path:
    """Get the images directory for a book, creating it if needed."""
    base_dir = Path(__file__).parent.parent.parent / "data" / "books" / book_slug / "images"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

def process_image(image_data: bytes, filename: str) -> bytes:
    """Process image: resize if needed, compress, convert to JPG."""
    try:
        img = Image.open(io.BytesIO(image_data))
        
        # Convert RGBA to RGB (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too wide
        if img.width > MAX_IMAGE_WIDTH:
            ratio = MAX_IMAGE_WIDTH / img.width
            new_height = int(img.height * ratio)
            img = img.resize((MAX_IMAGE_WIDTH, new_height), Image.Resampling.LANCZOS)
        
        # Save to bytes
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=IMAGE_QUALITY, optimize=True)
        return output.getvalue()
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")

@router.post("/{book_slug}/images")
async def upload_image(
    book_slug: str,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """Upload an image for a book."""
    
    # Validate file extension
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file
    content = await file.read()
    
    # Check size
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_IMAGE_SIZE / 1024 / 1024:.1f}MB"
        )
    
    # Process image (resize, compress, convert to JPG)
    processed_content = process_image(content, file.filename or "image.jpg")
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.jpg"
    
    # Save to disk
    images_dir = get_images_dir(book_slug)
    file_path = images_dir / unique_filename
    
    with open(file_path, 'wb') as f:
        f.write(processed_content)
    
    # Return URL
    url = f"/api/books/{book_slug}/images/{unique_filename}"
    
    return {
        "url": url,
        "filename": unique_filename,
        "size": len(processed_content)
    }

@router.get("/{book_slug}/images/{filename}")
async def get_image(book_slug: str, filename: str):
    """Serve an image file."""
    
    images_dir = get_images_dir(book_slug)
    file_path = images_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Security check: ensure file is within images directory
    if not file_path.resolve().is_relative_to(images_dir.resolve()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(file_path, media_type="image/jpeg")
