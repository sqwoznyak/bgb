from dotenv import load_dotenv
import os

load_dotenv()

youkassa_account_id = os.getenv("YOUKASSA_ACCOUNT_ID")
youkassa_secret_key = os.getenv("YOUKASSA_SECRET_KEY")

BOT_TOKEN = os.getenv("BOT_TOKEN")
