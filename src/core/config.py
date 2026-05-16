from dotenv import load_dotenv
import os

load_dotenv()

class __Config:
    def __init__(self):
        pass

    def get_database_url(self):
        return os.getenv("DATABASE_URL")
    
    def get_sender_email(self):
        return os.getenv("SENDER_EMAIL")
    
    def get_email_app_password(self):
        return os.getenv("EMAIL_APP_PASSWORD")
    
    def get_base_url(self):
        return os.getenv("BASE_URL")
    
    def get_origins(self):
        return os.getenv("ORIGINS")
    


config = __Config()