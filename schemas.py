from pydantic import BaseModel, Field
from typing import Optional

class PropertyRequest(BaseModel):
    price: Optional[float] = Field(
        default=None,
        description="The maximum ANNUAL rental budget in AED. "
            "1. If the user explicitly says monthly, multiply by 12. "
            "2. If the user provides a raw number under 20000 (e.g., '6000' or '8000'), assume it is a monthly budget and multiply it by 12. "
            "3. If the number is 20000 or higher, assume it is already an annual budget.")
    location: Optional[str] = Field(default=None, description="The neighborhood, area, Emirate or city mentioned.")
    bedrooms: Optional[int] = Field(default=None, description="The number of bedrooms. "
            "If the user provides a standalone low integer (e.g., '1', '2', '3', '4', '5'), "
            "you MUST assume it represents the number of bedrooms.")
    wants_to_view: Optional[bool] = Field(
        default=False,
        description="Set to True ONLY if the user explicitly asks to view a property, book a viewing, or speak to an agent.")

class PropertyBase(BaseModel):
    title: str
    description: str
    price: float
    location: str 
    bedrooms: int 

class PropertyCreate(PropertyBase):
    pass

class PropertyResponse(PropertyBase):
    id: int

class PropertyUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    price: Optional[float]
    location: Optional[str] 
    bedrooms: Optional[int] 
