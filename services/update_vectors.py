from models import SessionLocal
from ai_services import get_embedding
from models import Property
# Make sure to import your specific embedding function here!
# from services.openai_service import get_embedding 

def upgrade_embeddings():
    db = SessionLocal()
    try:
        # 1. Fetch all existing properties (Images and data remain untouched)
        properties = db.query(Property).all()
        
        print(f"Found {len(properties)} properties. Upgrading vectors...")
        
        for prop in properties:
            # 2. Construct the new, highly detailed semantic string
            text_to_embed = f"A {prop.bedrooms} bedroom rental property in {prop.location} for {prop.price} AED annually. {prop.description}"
            
            # 3. Ask OpenAI to vectorize this new string
            new_vector = get_embedding(text_to_embed)
            
            # 4. Overwrite ONLY the embedding column in memory
            prop.embedding = new_vector
            print(f"Updated vector for: {prop.title}")
            
        # 5. Commit the updates to the database
        db.commit()
        print("✅ All embeddings successfully upgraded!")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    upgrade_embeddings()