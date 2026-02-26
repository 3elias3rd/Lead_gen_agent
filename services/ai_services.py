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
    # TIER 1 STRICT MATCHING
    base_query = db.query(Property).order_by(Property.embedding.cosine_distance(query_vector))

    # TIER 1 STRICT MATCHING
    # Add filter if data exists
    if search_restrictions.price is not None:
        base_query = base_query.filter(Property.price <= search_restrictions.price)

    if search_restrictions.location is not None:
        base_query = base_query.filter(Property.location.ilike(f"%{search_restrictions.location}%"))

    if search_restrictions.bedrooms is not None:
        base_query = base_query.filter(Property.bedrooms == search_restrictions.bedrooms)
    
    exact_matches = base_query.limit(limit).all()

    if exact_matches:
        # Return exact matches if they are found
        return exact_matches, "exact"
    
    # TIER 2: Ai fallback
    # Sentence of what the user wants
    user_preferences = f"A rental property in {search_restrictions.location} with {search_restrictions.bedrooms} bedrooms for under {search_restrictions.price} AED annually."

    # Generate an embedding for these preferences.
    query_vector = get_embedding(user_preferences)

    # Use Cosine distance to find the most similar apartments.
    fallback_matches = db.query(Property).order_by(Property.embedding.cosine_distance(query_vector)).limit(limit).all()

    # Return the fallback matches
    return fallback_matches, "fallback"
    
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

def generate_image(description) -> str:
    prompt = (
    f"A realistic, unedited daytime photograph of a standard residential property in the UAE. Taken on a smartphone by a real estate agent. Natural lighting, authentic, standard residential architecture, not glossy, not CGI, no hyper-realistic filters. Description: {description}"
    )

    result = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        response_format="url"
    )
    
    image_url = result.data[0].url

    return image_url
