from openai import OpenAI

import os
from sqlalchemy.orm import Session

from dotenv import load_dotenv

from models import UserSession

from schemas import PropertyRequest
from functions import get_embedding

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_relevant_properties(search_restrictions: PropertyRequest | UserSession, db: Session, limit = 3):
    from models import Property

    query_vector = get_embedding(f"A {search_restrictions.bedrooms} bedroom property for {search_restrictions.price} in {search_restrictions.location}")

    # Order Properties table by embedding similarity to the query embedding.
    base_query = db.query(Property).order_by(Property.embedding.cosine_distance(query_vector))

    # Add filter if data exists
    if search_restrictions.price is not None:
        base_query = base_query.filter(Property.price <= search_restrictions.price)

    if search_restrictions.location is not None:
        base_query = base_query.filter(Property.location.ilike(f"%{search_restrictions.location}%"))

    if search_restrictions.bedrooms is not None:
        base_query = base_query.filter(Property.bedrooms == search_restrictions.bedrooms)

    return base_query.limit(limit).all()
    
def generate_restrictions(user_input: str):

    system_prompt = "extract the property information."

    response = client.responses.parse(
        
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_input,
            },
        ],
        text_format=PropertyRequest
    )

    search_restrictions = response.output_parsed

    return search_restrictions

def generate_image(location, bedrooms) -> str:
    prompt = (
    f"Photorealistic image of a luxury {bedrooms}-bedroom apartment in {location}, "
    "Dubai. Modern high-end architecture, floor-to-ceiling glass windows, city skyline view, "
    "sunlit interiors, sleek contemporary furniture, ultra-realistic lighting, 8K resolution, "
    "professional architectural photography style."
    )

    result = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        response_format="url"
    )
    
    image_url = result.data[0].url

    return image_url
