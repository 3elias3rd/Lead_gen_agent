from pydantic import BaseModel, Field
from typing import Optional

class PropertyRequest(BaseModel):
    price: Optional[float] = Field(default=None, description="The neighborhood, area, or city mentioned.")
    location: Optional[str] = Field(default=None, description="The maximum budget or price.")
    bedrooms: Optional[int] = Field(default=None, description="The number of bedrooms.")

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


