# UAE Lead Qualification Bot

A WhatsApp based real estate assistant that is designed to help customers find the best property available from their personal criteria. This effectively automates the discovery stage and allows the real estate agents to save time and filter low quality leads, effectively improving their daily workflow. To build the assistant I used Python, FastAPI and PostgreSQL. The bot uses LLM intent extraction and vector search to match the users criteria with the listings available within the database.

### 🧠 Stateful Conversation Memory (Solving Webhook Amnesia)
Early on I found out that a major problem in building a SMS/WhatsApp agents is statelessness. Initially if the user asked for "a place in Downtown Dubai for 4800 AED a month", the bot would extract `{"location": "Downtown Dubai", "price": 48000}`. After realizing that the bedrooms field was missing, it would send a prompt back to the user asking for the missing information. At this point if the user replied with "2", the bot would now extract `{"bedrooms": 2}` and forget about the previous location and price input. This would lead to it now asking the user for previously provided information in an infinite loop.

**The Solution:** 
I implemented stateful conversation memory using PostgreSQL. Now, whenever data is extracted via Pydantic, it is **upserted** into a `user_session` table using the user's phone number as the primary key. This allows the backend to incrementally build the user's search criteria across multiple asynchronous messages—updating or inserting data as the conversation naturally flows.

### 🔍 Two-Tier Search Engine (Preventing Lost Leads)
In the first iteration of this agent, the system relied on strict SQL exact-matching. If a user queried a specific location and price, and the database didn't have a perfect match, the bot would hit a dead end and return: "Sorry, a match could not be found." This was a major problem because in real estate a dead end like this one could lose you the lead.

**The Solution:** 
I upgraded the matching engine to use vector similarity search via `pgvector`. The backend now takes the user's extracted preferences (location, budget, bedrooms), dynamically slots them into a natural language sentence, and generates an OpenAI vector embedding. This embedding is then compared against the property database using cosine distance, allowing the bot to always return the 3 *closest* properties, ensuring the user always receives high-quality alternatives.

### Smart intent extraction  (Handling unpredictable human input)
A major problem with the conversational UI is how unpredictable human text can be. At first to extract user intent the bot would require the user to clearly state that “my maximum price is 72000 AED”. If a user naturally replied to a budget prompt by only typing “6000” as a monthly budget for rent, the bot would fail to match the intent, ultimately leaving the price field emply..

**The solution**
I engineered as secondary intent extraction layer, using an LLM and pydantic schemas to account for this unpredictability. To fix this, I programmed a set of smart, conditional rules directly into the AI's data extraction process: 
* Raw numbers under 20,000 are to be extracted as the users monthly budget and then automatically multiplied by 12 to match the database pricing structure
* Raw numbers above 20,000 are to be extracted as the user annual budget.
* Raw single digit integers are to be extracted as the prefered amount of bedrooms. 

This allowed the UX to become user friendly, whilst also alowing the backend to silently  standardize the users messy text into clean quariable database parameters.

### Design Desisions and pivots: Generative AI vs Authentic UX
To complete Lead Qualification Bot I needed to show the customer the images of the of the properties that matched their criteria. The problem here, is that sourcing the required images raised a lot of strict copyright and privacy constraints. 

* **My initial approach:** To bypass copyright laws I decided to turn to OpenAi's DALL-3 E to generate images of apartments using the aparments description. 
* **The realization** Althoug the approach worke and resulted in a more complete UX. The images felt fake and even off putting effectively dongrading the users experience. 
* **The pivot:** I swapped out the fake looking AI images for authentic, high quality images using Pexels' free licensing model to ensure legal compliance. Instead of hardcoding URLs, I built an automated pipeline that would ingest a Pexels image, dynamically detect its MIME type (handling JPEG vs Webps), and then securely hosts it in a dedicated AWS s3 bucket. This allow the bot to deliver permanent meadia payloads via Twilio.

## Installation

**Prerequisites**
Docker and docker compose
An active Twilio Sandbox, Open API Key, and AWS S3 Bucket
Ngrok (for exposing the local server to Twilio)


1. Clone the repository
git clone https://github.com/yourusername/lead-generation-bot.git
*cd lead-generation-bot*

2. Configure Environment Variables
create a .env file in the root directory and add your external API Keys:

OPENAI_API_KEY=your_openai_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_NUMBER=whatsapp:+14155238886
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
DATABASE_URL=postgresql://properties_db_owner:password@db:5432/properties_db

3. Build and Run the Containers
*docker-compose up --build -d*

4. Seed the Database
Once the containers are running, execute the seeding script to pull the Pexels images, generate the OpenAI vector embedding in order to populate your local database.
*docker-compose exec api python seed_to_db.py*

5. Connect Twilio
Expose your local port 8000 using Ngrok, and paste the generated HTTPS URL (Labeled forwarding URL) into your Twilio Whatsapp Sandbox configuration. Append **/replywhatsapp** to the end of the url.
