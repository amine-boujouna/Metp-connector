import os
from dotenv import load_dotenv

load_dotenv()  
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "meta_data")

if not ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
    raise Exception("ACCESS_TOKEN et FACEBOOK_PAGE_ID doivent être définis dans les variables d'environnement")

