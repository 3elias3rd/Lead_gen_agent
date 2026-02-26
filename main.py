from fastapi import FastAPI, Form, BackgroundTasks, Depends
from fastapi.responses import Response
from twilio.rest import Client

from sqlalchemy.orm import Session
from sqlalchemy import delete

from typing import Annotated
import os

from services.ai_services import generate_restrictions, get_relevant_properties
from models import update_session, UserSession, send_whatsapp, get_db, SessionLocal

from dotenv import load_dotenv

load_dotenv()
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
client = Client(account_sid, auth_token)

app = FastAPI()

@app.get("/")
def homepage():
      return "Hello"

@app.post("/reply_whatsapp")
async def reply_whatsapp(
      From_number: Annotated[str, Form(alias="From")], Body: Annotated[str, Form()], background_task: BackgroundTasks):
     
      background_task.add_task(create_message, From_number, Body)

      return Response(content=str("<Response></Response>"), media_type="text/xml")


async def create_message(From_number: str, message: str):
      db = SessionLocal()
      try:
            # Reset logic
            if message.lower() in ["reset", "start over", "restart"]:
                  stmt = delete(UserSession).where(UserSession.phone_number==From_number)
                  db.execute(stmt)
                  db.commit()

                  return send_whatsapp(to=From_number, text="Session has been reset, what kind of property are you looking for?")
            
            greetings = ["hi", "hello", "hey", "yo", "start", "good morning", "good evening"]
            if message.lower().strip() in greetings:
                  user_state = db.query(UserSession).filter(UserSession.phone_number==From_number).first()

                  # Welcome back
                  if user_state and any([user_state.location, user_state.bedrooms, user_state.price]):
                        return send_whatsapp(
                              to=From_number,
                              text="Welcome back! 👋 Would you like to start searching for your next home?")
                  
                  else:
                        return send_whatsapp(
                              to=From_number,
                              text="Hello! 👋 I'm your AI Real Estate Assistant. I can help you find the perfect property across the UAE. To get started, what specific area are you looking in?"
                        )

            # Extract intent from initial user message
            new_intent = generate_restrictions(user_input=message)

            # Update DB memory and return it
            user_state = update_session(phone_number=From_number, data=new_intent, db=db)

            # Check if anything is missing from the memory
            if not user_state.location:
                  return send_whatsapp(to=From_number, text ="What area in Dubai are you looking for?")
            
            if not user_state.price:
                  return send_whatsapp(to=From_number, text="What is your maximum price?")
            
            if not user_state.bedrooms:
                  return send_whatsapp(to=From_number, text="How many bedrooms are you looking for?")
            
            # Query db for relevant properties
            relevant_properties = get_relevant_properties(search_restrictions=user_state, db=db)

            if not relevant_properties:
                  return send_whatsapp(to=From_number, text="I couldn't find properties matching your criteria. Try a different area or budget.")

            send_whatsapp(to=From_number, text="Here are the best matches :\n")
            
            for property in relevant_properties:
                  
                  line = f"{property.title}, location: {property.location}, bedrooms:{property.bedrooms}, price: {property.price:,.0f}"
                  send_whatsapp(to=From_number, text=line, image_url=property.image_url)
            
            send_whatsapp(to=From_number, text="\nWould you like more details on any of these?")
      
      finally:
            db.close()
      