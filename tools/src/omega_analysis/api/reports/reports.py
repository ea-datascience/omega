"""Reports module placeholder."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def reports_placeholder():
    """Placeholder endpoint for reports functionality."""
    return {"message": "Reports endpoints - coming soon", "status": "not_implemented"}