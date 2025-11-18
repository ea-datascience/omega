"""Architecture module placeholder."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def architecture_placeholder():
    """Placeholder endpoint for architecture functionality."""
    return {"message": "Architecture endpoints - coming soon", "status": "not_implemented"}