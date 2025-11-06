import psycopg2
from dotenv import load_dotenv
import os

# .env dosyasını yükle
load_dotenv()

# Bağlantı fonksiyonu
def baglanti_olustur():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

# veritabani.py dosyası içinde, tablo_olustur fonksiyonu

# 1️⃣ Tablo oluşturma
# veritabani.py dosyası içinde, tablo_olustur fonksiyonu

def tablo_olustur():
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        
        # 1. KULLANICILAR Tablosu (Diyetisyen ve Danışanlar)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id SERIAL PRIMARY KEY,
                ad VARCHAR(50) NOT NULL,
                soyad VARCHAR(50) NOT NULL,
                eposta VARCHAR(100) UNIQUE NOT NULL,
                sifre_hash VARCHAR(255) NOT NULL, -- Şifre Güvenliği için
                dogum_tarihi DATE,
                cinsiyet VARCHAR(10),
                rol VARCHAR(20) NOT NULL CHECK (rol IN ('Diyetisyen', 'Danışan')),
                olusturma_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. YEMEKLER Tablosu (Kalori Veritabanı)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS yemekler (
                id SERIAL PRIMARY KEY,
                yemek_adi VARCHAR(100) NOT NULL UNIQUE,
                kalori_100gr NUMERIC(5, 2) NOT NULL,
                protein_100gr NUMERIC(5, 2),
                yag_100gr NUMERIC(5, 2),
                karbonhidrat_100gr NUMERIC(5, 2),
                kategori VARCHAR(50) 
            );
        """)

        # 3. DANISAN HEDEFLERİ Tablosu
        cur.execute("""
            CREATE TABLE IF NOT EXISTS danisan_hedefleri (
                id SERIAL PRIMARY KEY,
                danisan_id INTEGER REFERENCES kullanicilar(id) ON DELETE CASCADE,
                baslangic_kilo NUMERIC(5, 2) NOT NULL,
                hedef_kilo NUMERIC(5, 2) NOT NULL,
                hedef_kalori_gunluk NUMERIC(5, 2),
                hedef_baslangic_tarihi DATE DEFAULT CURRENT_DATE,
                hedef_durumu VARCHAR(20) CHECK (hedef_durumu IN ('Aktif', 'Tamamlandı', 'Pasif')) DEFAULT 'Aktif'
            );
        """)
        
        # 4. TAKİP KAYITLARI Tablosu (Günlük Tüketilen Yemekler)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS takip_kayitlari (
                id SERIAL PRIMARY KEY,
                danisan_id INTEGER REFERENCES kullanicilar(id) ON DELETE CASCADE,
                yemek_id INTEGER REFERENCES yemekler(id) ON DELETE RESTRICT,
                porsiyon_gram INTEGER NOT NULL,
                tuketim_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        print("✅ Tüm proje tabloları başarıyla oluşturuldu!")
    
    except Exception as e:
        print("❌ Tablo oluşturulamadı (SQL Hata Mesajı):", e)
    finally:
        if cur: cur.close()
        if conn: conn.close()


# Ana akış (mevcut dosyanızda zaten var)
if __name__ == "__main__":
    tablo_olustur()
    # ... diğer fonksiyon çağrıları ...

# 2️⃣ Veri ekleme
def veri_ekle(ad, email):
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (name, email)
            VALUES (%s, %s)
        """, (ad, email))
        conn.commit()
        print(f"✅ {ad} adlı kullanıcı başarıyla eklendi!")
    except Exception as e:
        print("❌ Veri eklenemedi:", e)
    finally:
        cur.close()
        conn.close()

# 3️⃣ Verileri listeleme
def verileri_goster():
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users ORDER BY id;")
        veriler = cur.fetchall()

        print("\n📋 Kayıtlı Kullanıcılar:")
        for v in veriler:
            print(f"ID: {v[0]} | İsim: {v[1]} | E-posta: {v[2]} | Kayıt tarihi: {v[3]}")

        if not veriler:
            print("Henüz kullanıcı yok.")
    except Exception as e:
        print("❌ Veriler alınamadı:", e)
    finally:
        cur.close()
        conn.close()

# 🔹 Ana akış
if __name__ == "__main__":
    tablo_olustur()  # tabloyu oluşturur (yoksa)
    veri_ekle("Kardelen Avcı", "kardelen@example.com")  # örnek kayıt
    verileri_goster()  # tüm verileri göster
