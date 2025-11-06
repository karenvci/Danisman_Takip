import psycopg2
from dotenv import load_dotenv
import os

# .env dosyasını yükle
load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    print("✅ Bağlantı başarılı!")
    conn.close()
except Exception as e:
    print("❌ Bağlantı hatası:", e)
#