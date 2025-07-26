from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from services import JessAIService
from database import get_db
from schemas import UserMessage
from config import settings
import logging

app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Jess AI starting up...")

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    db=Depends(get_db)
):
    form_data = await request.form()
    phone = form_data.get("From", "").replace("whatsapp:", "")
    message = form_data.get("Body", "")
    
    service = JessAIService(db)
    response = await service.process_message(phone, message)
    
    return JSONResponse(content={"response": response})

@app.post("/api/train")
async def train_reply(
    data: UserMessage,
    db=Depends(get_db)
):
    service = JessAIService(db)
    result = service.train_reply(data.phone, data.trigger, data.response)
    return {"status": "success", "data": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
