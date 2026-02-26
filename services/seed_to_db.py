from sqlalchemy.orm import Session

from models import Property, upload_to_s3, SessionLocal

from services.ai_services import generate_image, get_embedding


def property_to_db(title, price, location, bedrooms, description, db: Session):

    image_url = generate_image(location=location, bedrooms=bedrooms)

    aws_url = upload_to_s3(image_url=image_url)

    embedding = get_embedding(description)

    property = Property(title=title, description=description, price=price, location=location, bedrooms=bedrooms, embedding=embedding, image_url=aws_url)

    db.add(property)

    db.commit()

    db.refresh(property)

    return property

dummy_properties = dummy_properties = [
    {
        "title": "Ultra-Luxury Palm Villa",
        "description": "Exclusive 6-bedroom beachfront signature villa on Palm Jumeirah. Features a private infinity pool, private beach access, home cinema, and fully upgraded contemporary interiors.",
        "price": 35000000,
        "location": "Palm Jumeirah",
        "bedrooms": 6
    },
    {
        "title": "Al Majaz Lagoon Penthouse",
        "description": "Elegant full-floor penthouse in Sharjah overlooking the Khalid Lagoon. High-end interiors, massive wrap-around balconies, and walking distance to Al Majaz Waterfront.",
        "price": 4200000,
        "location": "Al Majaz",
        "bedrooms": 4
    },
    {
        "title": "Affordable JVC Studio",
        "description": "Cozy, fully furnished studio apartment in Jumeirah Village Circle. Perfect for young professionals. Building features a shared gym, swimming pool, and close proximity to the circle mall.",
        "price": 450000,
        "location": "JVC",
        "bedrooms": 0
    },
    {
        "title": "Downtown Burj View Apartment",
        "description": "Modern 2-bedroom high-rise apartment in Downtown Dubai offering unobstructed views of the Burj Khalifa and Dubai Fountains. Direct access to the mall.",
        "price": 4500000,
        "location": "Downtown Dubai",
        "bedrooms": 2
    },
    {
        "title": "Spacious Arabian Ranches Townhouse",
        "description": "Family-friendly 3-bedroom townhouse in Arabian Ranches. Features an open-plan kitchen, landscaped private garden, maid's room, and access to the community golf course.",
        "price": 3100000,
        "location": "Arabian Ranches",
        "bedrooms": 3
    },
    {
        "title": "Dubai Marina Waterfront Flat",
        "description": "Sleek 1-bedroom apartment in Dubai Marina. Floor-to-ceiling windows with direct marina views, modern appliances, and walking distance to the metro and Marina Walk.",
        "price": 1400000,
        "location": "Dubai Marina",
        "bedrooms": 1
    },
    {
        "title": "Al Zahia Premium Villa",
        "description": "Brand new 5-bedroom luxury villa in Sharjah's premier gated community. Features smart home tech, a large backyard ready for a pool, and premium marble flooring.",
        "price": 5500000,
        "location": "Al Zahia",
        "bedrooms": 5
    },
    {
        "title": "Business Bay Executive Suite",
        "description": "Premium 2-bedroom apartment in Business Bay designed for executives. Close to DIFC, featuring a dedicated home office space and panoramic Dubai Canal views.",
        "price": 2800000,
        "location": "Business Bay",
        "bedrooms": 2
    }
]

db = SessionLocal()
try:
    for prop in dummy_properties:
        exists = db.query(Property).filter(Property.title == prop["title"]).first()
        if not exists:
            property_to_db(**prop, db=db)
        else:
            print(f"Skipping {prop['title']} - already exists")
finally:
    db.close()

