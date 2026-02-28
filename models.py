from sqlalchemy import create_engine, String, Float, Integer, text, DateTime, func, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.dialects.postgresql import insert

from pgvector.sqlalchemy import Vector

from twilio.rest import Client

import uuid

# AWS imports
import boto3

import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional
import requests

from schemas import PropertyRequest

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
client = Client(account_sid, auth_token)

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Base(DeclarativeBase):
    pass

class Property(Base):
    __tablename__ = "properties"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    location: Mapped[str] = mapped_column(String)
    bedrooms: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[Vector] = mapped_column(Vector(1536))
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

class UserSession(Base):
    __tablename__ = "user_session"
    phone_number: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bedrooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

def create_tables():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    Base.metadata.create_all(engine)
    print("All tables created")

def update_session(phone_number: str, data: PropertyRequest, db: Session):

    try:
        # Take the raw dictionary
        new_data = data.model_dump()

        # Clean data
        clean_data = {
            key: value
            for key, value in new_data.items()
            if value not in [None, "", "unknown", "N/A", "/", 0]
        }


        # Safety check
        if not clean_data:
            user_state = db.query(UserSession).filter(UserSession.phone_number==phone_number).first()
            return user_state

        insert_values = {"phone_number": phone_number, **clean_data}

        insert_stmt = insert(UserSession).values(**insert_values)

        upsert = insert_stmt.on_conflict_do_update(
            index_elements=["phone_number"],
            set_={
                key: getattr(insert_stmt.excluded, key)
                for key in clean_data.keys()
            }
        )

        db.execute(upsert)
        db.flush()

        db.commit()
        user_state = db.query(UserSession).filter(UserSession.phone_number==phone_number).first()
        return user_state
    
    except Exception as e:
        db.rollback()
        raise e

    
def send_whatsapp(to: str, text: str, image_url: Optional[str] = None):

    clean_to = to.replace("whatsapp:", "")
    clean_from = TWILIO_NUMBER.replace("whatsapp:", "")

    message_data = {
        "from_": f"whatsapp:{clean_from}",
        "to":f"whatsapp:{clean_to}",
        "body": text}

    if image_url:
        message_data["media_url"] = [image_url]

    formatted_response = client.messages.create(**message_data)
        
    return formatted_response

    
def upload_to_s3(image_url: str):
    # Get response from pexels
    response = requests.get(image_url)

    # Get the content type (image/jpeg or image/png)
    content_type = response.headers.get('Content-Type', 'image/png')
    image_bytes = response.content

    # Determine correct file extention for s3 key
    extention = content_type.split('/')[-1]
    unique_id = str(uuid.uuid4())
    object_name = f"property_{unique_id}.{extention}"

    bucket_name = "lead-bot-bucket"
        
    s3 = boto3.client('s3', region_name='eu-north-1')

    # Pass content type to s3
    s3.put_object(
        Bucket=bucket_name,
        Key=object_name,
        Body=image_bytes,
        ACL='public-read',
        ContentType=content_type)

    return f"https://{bucket_name}.s3.eu-north-1.amazonaws.com/{object_name}"

create_tables()