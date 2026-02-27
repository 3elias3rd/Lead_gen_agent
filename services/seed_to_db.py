from sqlalchemy.orm import Session

from models import Property, upload_to_s3, SessionLocal

from services.ai_services import generate_image, get_embedding


def property_to_db(title: str, price: float, location: str, bedrooms:int, description: str, db: Session) -> Property:

    image_url = generate_image()

    aws_url = upload_to_s3(image_url=image_url)

    embedding = get_embedding(f"A {bedrooms} bedroom rental property in {location} for {price} AED annually. {description}")

    property = Property(title=title, description=description, price=price, location=location, bedrooms=bedrooms, embedding=embedding, image_url=aws_url)

    db.add(property)

    db.commit()

    db.refresh(property)

    return property

dummy_properties = dummy_properties = [
    {
        "title": "Cozy Al Nahda Studio",
        "description": "A clean, well-maintained studio apartment in Al Nahda, Sharjah. Features a standard closed kitchen, built-in wardrobes, and easy access to the Dubai border. Ideal for a single professional.",
        "price": 36000,
        "location": "Al Nahda",
        "bedrooms": 1
    },
    {
        "title": "Al Majaz Lagoon View 2BR",
        "description": "Spacious 2-bedroom family apartment in Al Majaz, Sharjah. Features a large balcony with partial lagoon views, a semi-open kitchen, and walking distance to Al Majaz park.",
        "price": 55000,
        "location": "Al Majaz",
        "bedrooms": 2
    },
    {
        "title": "Bright JVC 1 Bedroom Flat",
        "description": "Standard 1-bedroom apartment in Jumeirah Village Circle (JVC). Features a practical open-plan living area, a shared community pool, and dedicated covered parking.",
        "price": 65000,
        "location": "JVC",
        "bedrooms": 1
    },
    {
        "title": "Silicon Oasis Family 2BR",
        "description": "Comfortable 2-bedroom apartment in Dubai Silicon Oasis. Features a large living room, closed kitchen with standard fittings, and close proximity to community supermarkets and clinics.",
        "price": 90000,
        "location": "Dubai Silicon Oasis",
        "bedrooms": 2
    },
    {
        "title": "Dubai Marina 1BR with Balcony",
        "description": "A practical 1-bedroom apartment in a standard Dubai Marina tower. Features a small balcony overlooking the street, fitted kitchen appliances, and a 5-minute walk to the Metro.",
        "price": 110000,
        "location": "Dubai Marina",
        "bedrooms": 1
    },
    {
        "title": "Damac Hills 2 Townhouse",
        "description": "A standard 3-bedroom townhouse in Damac Hills 2. Features a private backyard, open-concept kitchen, utility room, and access to the community parks and sports facilities.",
        "price": 140000,
        "location": "Damac Hills 2",
        "bedrooms": 3
    },
    {
        "title": "Downtown Dubai 2BR Apartment",
        "description": "Well-lit 2-bedroom apartment in Downtown Dubai. Standard modern finishes, en-suite bathrooms, a decent-sized balcony, and walking distance to the Boulevard.",
        "price": 165000,
        "location": "Downtown Dubai",
        "bedrooms": 2
    },
    {
        "title": "Dubai Creek Harbour 3BR",
        "description": "Spacious 3-bedroom apartment in Dubai Creek Harbour. Features contemporary standard finishing, a spare room, and community views. Great for larger families.",
        "price": 180000,
        "location": "Dubai Creek Harbour",
        "bedrooms": 3
    },
    {
        "title": "Muwaileh Commercial 1BR",
        "description": "A very practical 1-bedroom apartment in Muwaileh Commercial, Sharjah. Close to the university city. Features a standard closed kitchen, and street parking.",
        "price": 38000,
        "location": "Muwaileh",
        "bedrooms": 1
    },
    {
        "title": "International City Budget Studio",
        "description": "Standard studio apartment in the England Cluster of International City. Very basic finishing, built-in wardrobes, and close to local retail shops. Ideal for someone looking for a highly affordable Dubai base.",
        "price": 36000,
        "location": "International City",
        "bedrooms": 0
    },
    {
        "title": "Al Taawun 3-Bedroom Family Home",
        "description": "A large 3-bedroom apartment in Al Taawun, Sharjah. Older building but well-maintained, featuring a utility room, large closed kitchen, and easy access to the Dubai border for commuters.",
        "price": 75000,
        "location": "Al Taawun",
        "bedrooms": 3
    },
    {
        "title": "Discovery Gardens 2BR",
        "description": "Spacious 2-bedroom apartment in Discovery Gardens. Features a standard open kitchen, community park views, and walking distance to the Metro pavilion.",
        "price": 80000,
        "location": "Discovery Gardens",
        "bedrooms": 2
    },
    {
        "title": "Al Furjan Modern 2BR",
        "description": "A clean, newly handed-over 2-bedroom apartment in Al Furjan. Features contemporary finishing, a shared gym and pool, and a balcony overlooking the residential community.",
        "price": 85000,
        "location": "Al Furjan",
        "bedrooms": 2
    },
    {
        "title": "JLT 1BR High-Rise",
        "description": "Standard 1-bedroom apartment in Jumeirah Lake Towers (JLT). Features a semi-open kitchen, partial lake views, and a 5-minute walk to the DMCC metro station. Great for young professionals.",
        "price": 95000,
        "location": "JLT",
        "bedrooms": 1
    },
    {
        "title": "Dubai South 3BR Townhouse",
        "description": "A brand new, standard 3-bedroom townhouse in Dubai South. Features a private covered garage, a small backyard, and access to emerging community amenities near the Al Maktoum Airport.",
        "price": 120000,
        "location": "Dubai South",
        "bedrooms": 3
    },
    {
        "title": "Sharjah Sustainable City Villa",
        "description": "Modern 3-bedroom eco-friendly villa in Sharjah Sustainable City. Features solar panels, smart AC controls, an open-plan living area, and a private garden.",
        "price": 130000,
        "location": "Sharjah Sustainable City",
        "bedrooms": 3
    },
    {
        "title": "Dubai Hills Estate 2BR",
        "description": "A premium 2-bedroom apartment in Dubai Hills Estate. Features high-quality standard finishing, direct views of the central park, and close proximity to the Dubai Hills Mall.",
        "price": 150000,
        "location": "Dubai Hills Estate",
        "bedrooms": 2
    },
    {
        "title": "Shoreline Palm Jumeirah 1BR",
        "description": "A classic 1-bedroom apartment in the Shoreline buildings on Palm Jumeirah. Older but well-kept standard finishing, with included access to the private beach club and gym.",
        "price": 160000,
        "location": "Palm Jumeirah",
        "bedrooms": 1
    },
    {
        "title": "Al Hamra Village 2BR Apartment",
        "description": "A standard 2-bedroom open-plan apartment in Al Hamra Village. Features white walls, light wood flooring, and a small living area. The view from the kitchen shows basic grey cabinetry and a stainless steel refrigerator. Bright natural light coming from the balcony window.",
        "price": 75000,
        "location": "Ras Al Khaimah",
        "bedrooms": 2
    },
    {
        "title": "Al Qasba 1BR Canal View",
        "description": "A practical 1-bedroom apartment near Al Qasba. The living room has a standard layout with exposed AC vents on the ceiling and neutral tile flooring. Includes a closed kitchen with standard white countertops. Midday sunlight illuminating an unfurnished living space.",
        "price": 45000,
        "location": "Sharjah",
        "bedrooms": 1
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

