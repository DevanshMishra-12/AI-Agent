from dotenv import load_dotenv
import os

print("✅ Checking environment setup...")

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")

if openai_key:
    print("🔑 OPENAI_API_KEY found ✅")
else:
    print("❌ OPENAI_API_KEY not found ❗️Check your .env file")
