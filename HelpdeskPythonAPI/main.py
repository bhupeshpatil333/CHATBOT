from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import datetime
from pydantic import BaseModel
import uuid
import os
from difflib import SequenceMatcher

# --- DATABASE SETUP (SQLite) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./helpdesk.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FAQ(Base):
    __tablename__ = "faqs"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    answer = Column(String)
    keywords = Column(String)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    issue = Column(String)
    description = Column(String)
    status = Column(String, default="Open")
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

class ChatLog(Base):
    __tablename__ = "chatlogs"
    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(String)
    bot_response = Column(String)
    is_resolved = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Seed mock database FAQ
def seed_db():
    db = SessionLocal()
    # Force delete existing FAQs and re-seed to ensure the new keywords from the UI are active
    db.query(FAQ).delete()
    faqs = [
        # Network & VPN
        FAQ(question="VPN Connection Issue", answer="Disconnect and reconnect your VPN client. Ensure MFA is completed on your phone.", keywords="vpn,connecting,connect,connection,network"),
        FAQ(question="Network is slow", answer="Run a speed test. Restart your router or contact local IT if below 10Mbps.", keywords="network,slow,internet,speed"),
        FAQ(question="Wifi not connecting", answer="Forget the 'Company_Guest' network and reconnect using your AD credentials.", keywords="wifi,wireless,internet,connect"),
        
        # Hardware
        FAQ(question="Printer not working", answer="Ensure the printer is online. Restart the Print Spooler service on your PC.", keywords="printer,offline,working,print"),
        FAQ(question="Monitor not displaying", answer="Check the HDMI/DisplayPort cable. Press Win+P to ensure 'Extend' or 'Duplicate' is selected.", keywords="monitor,screen,display,black,blank"),
        FAQ(question="Laptop overheating", answer="Ensure vents aren't blocked. Close high-CPU apps in Task Manager.", keywords="heat,hot,overheating,fan,laptop"),
        
        # Software & ERP
        FAQ(question="ERP Login Problem", answer="Clear browser cache. Ensure your account isn't locked due to failed attempts.", keywords="erp,sap,oracle,login,issue"),
        FAQ(question="Outlook Syncing Issue", answer="Go to File -> Account Settings -> Repair. Restart Outlook.", keywords="outlook,sync,email,syncing"),
        FAQ(question="Teams keeps crashing", answer="Clear Teams cache: Delete folder %appdata%\Microsoft\Teams and restart.", keywords="teams,crash,crashing,microsoft"),
        FAQ(question="Excel is frozen", answer="Press Ctrl+Alt+Del, open Task Manager, and force end the Excel process.", keywords="excel,frozen,hang,stuck"),
        
        # Security & Password
        FAQ(question="Password Reset Request", answer="Visit https://auth.company.com/reset to change your AD/Office password.", keywords="password,reset,forgot,account"),
        FAQ(question="Suspicious Email / Phishing", answer="Do not click links. Use the 'Report Phish' button in Outlook immediately.", keywords="email,phishing,spam,suspicious,security"),
        FAQ(question="BitLocker Recovery Key", answer="Log in to your Microsoft account or contact IT support with your Recovery Key ID.", keywords="bitlocker,encryption,key,recovery,lock"),
        
        # Access & Accounts
        FAQ(question="New Software Request", answer="Submit a software request via the IT Self-Service portal under 'Software Catalog'.", keywords="software,request,install,download"),
        FAQ(question="Folder Access Denied", answer="Obtain approval from the folder owner/manager, then raise an 'Access Request' ticket.", keywords="access,folder,denied,permission,permission"),
        FAQ(question="Zoom account activation", answer="Sign in with SSO using your company email to activate your Pro license.", keywords="zoom,account,license,pro"),

        # Peripherals
        FAQ(question="Keyboard/Mouse not responding", answer="Replace batteries if wireless. Try a different USB port if wired.", keywords="mouse,keyboard,usb,peripheral"),
        FAQ(question="Headset mic not working", answer="Go to Sound Settings -> Input and ensure your headset is the default device.", keywords="headset,mic,microphone,audio,sound")
    ]
    db.add_all(faqs)
    db.commit()
    db.close()

seed_db()

# --- DIALOGFLOW SERVICE (Fallback safe) ---
def get_dialogflow_intent(text: str):
    try:
        from google.cloud import dialogflow
        project_id = os.getenv("DIALOGFLOW_PROJECT_ID", "your-dialogflow-project-id")
        session_id = str(uuid.uuid4())
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, session_id)
        
        text_input = dialogflow.TextInput(text=text, language_code="en-US")
        query_input = dialogflow.QueryInput(text=text_input)
        response = session_client.detect_intent(request={"session": session, "query_input": query_input})
        return response.query_result.fulfillment_text
    except Exception as e:
        # Failsafe if Google Credentials are not attached yet
        return "I'm having trouble connecting to my AI brain. Would you like to create a ticket?"

# --- FASTAPI APP ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class TicketRequest(BaseModel):
    issue: str
    description: str

@app.post("/api/chatbot/ask")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    bot_response = ""
    is_resolved = True
    user_msg = request.message.lower().strip()

    # 1. Local FAQ Machine - Smart Fuzzy Score Match
    faqs = db.query(FAQ).all()
    best_match = None
    highest_score = 0.0
    
    for faq in faqs:
        if not faq.keywords: continue
        kw_list = [k.strip().lower() for k in faq.keywords.split(",")]
        
        # Calculate max fuzzy score for this FAQ across all its keywords
        for kw in kw_list:
            # Check if keyword is in message OR if message is similar to keyword
            if kw in user_msg:
                score = 0.9 # High score for direct inclusion
            else:
                score = SequenceMatcher(None, kw, user_msg).ratio()
            
            if score > highest_score:
                highest_score = score
                best_match = faq

    # Threshold for "predictable" match (e.g. 0.6)
    if best_match and highest_score > 0.6:
        bot_response = best_match.answer
    else:
        # 2. AI Fallback (Simulated if no API key)
        bot_response = get_dialogflow_intent(user_msg)
        if not bot_response:
             bot_response = "I'm having trouble connecting to my AI brain. Would you like to create a ticket?"
             is_resolved = False
        else:
             # Autonomous Learning Engine: Save AI responses to local DB
             # Extracts unique words as keywords to answer similar queries in the future locally
             keywords = ",".join(set(user_msg.replace("?", "").split()))
             new_faq = FAQ(question=user_msg, answer=bot_response, keywords=keywords)
             db.add(new_faq)

    # 3. Learning System Log
    log = ChatLog(user_query=request.message, bot_response=bot_response, is_resolved=is_resolved)
    db.add(log)
    db.commit()

    return {"response": bot_response, "showTicketOption": not is_resolved}


@app.post("/api/ticket")
def create_ticket(request: TicketRequest, db: Session = Depends(get_db)):
    ticket = Ticket(issue=request.issue, description=request.description)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return {"message": "Ticket created successfully!", "ticketId": ticket.id}

@app.get("/api/kb")
def get_kb(db: Session = Depends(get_db)):
    return db.query(FAQ).all()

@app.get("/api/ticket")
def get_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).order_by(Ticket.created_date.desc()).all()
    return tickets
