# main.py

from fastapi import FastAPI, Query, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
from model import recommend, output_recommended_recipes
import razorpay
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv

from sqlalchemy.orm import Session

from signup import router as signup_router
from login import router as login_router

from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Razorpay setup
akey = os.getenv("APIKEY")
skey = os.getenv("SECRETKEY")

client = razorpay.Client(auth=(akey, skey))

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Database model and schemas are initialized in their respective modules

# Include signup and login routers
app.include_router(signup_router)
app.include_router(login_router)

# Load dataset
# Adjust the path as necessary
dataset = pd.read_csv('../Data/food1.csv')
dataset.info()

# Pydantic Model

class Params(BaseModel):
    n_neighbors: int = 5
    return_distance: bool = False

class Recipe(BaseModel):
    Name: str
    CookTime: str
    PrepTime: str
    TotalTime: str
    RecipeIngredientParts: List[str]
    Calories: float
    FatContent: float
    SaturatedFatContent: float
    CholesterolContent: float
    SodiumContent: float
    CarbohydrateContent: float
    FiberContent: float
    SugarContent: float
    ProteinContent: float
    RecipeInstructions: List[str]

class PredictionIn(BaseModel):
    nutrition_input: List[float] = Field(..., min_items=9, max_items=9)
    ingredients: List[str] = []
    params: Optional[Params] = None

class PredictionOut(BaseModel):
    output: Optional[List[Recipe]] = None

class PaymentRequest(BaseModel):
    amount: int  # Amount in INR (e.g., 99 for ₹99)
    email: str
    contact: str

# Dependency to get DB session (if needed)
from database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions for JWT

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Here you can fetch the user from DB if needed
    # For simplicity, we assume the token is valid
    return username

# Existing Endpoints

@app.get("/")
def home():
    return {"health_check": "OK"}

@app.post("/predict/", response_model=PredictionOut)
def update_item(prediction_input: PredictionIn, current_user: str = Depends(get_current_user)):
    """
    Endpoint to get recipe recommendations based on nutrition and ingredients.
    """
    recommendation_dataframe = recommend(
        dataset, 
        prediction_input.nutrition_input, 
        prediction_input.ingredients, 
        prediction_input.params.dict() if prediction_input.params else {}
    )
    output = output_recommended_recipes(recommendation_dataframe)
    if output is None:
        return {"output": None}
    else:
        return {"output": output}

@app.post("/create_payment_link/")
def create_payment_link(payment: PaymentRequest, current_user: str = Depends(get_current_user)):
    """
    Endpoint to create a Razorpay payment link.
    """
    try:
        # Convert amount to paise (₹1 = 100 paise)
        amount_in_paise = payment.amount * 100

        # Razorpay Payment Link API call
        response = client.payment_link.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "accept_partial": False,
            "description": "RecoMaster Subscription",
            "customer": {
                "email": payment.email,
                "contact": payment.contact
            },
            "notify": {
                "sms": True,
                "email": True
            },
            "reminder_enable": True,
            "callback_url": "http://localhost:8080/payment_success",  # Adjust as needed
            "callback_method": "get"
        })

        # Log or return the response for debugging
        logging.info(f"Payment link creation response: {response}")
        return {"payment_link": response['short_url']}
    
    except Exception as e:
        # Log the error to understand what's going wrong
        logging.error(f"Error while creating payment link: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Example Protected Endpoint (Optional)
@app.get("/protected/")
def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello, {current_user}! This is a protected route."}

# Payment Success Callback (Optional)
@app.get("/payment_success")
def payment_success():
    return {"message": "Payment was successful."}

# If running directly, include the following line to start the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
