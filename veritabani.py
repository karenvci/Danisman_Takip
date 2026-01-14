import psycopg2
from dotenv import load_dotenv
import os
import bcrypt 
from datetime import date, timedelta 

load_dotenv()

def baglanti_olustur():
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
    except Exception as e:
        print(f"Baglanti hatasi: {e}")
        raise

def tablo_olustur():
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id SERIAL PRIMARY KEY,
                ad VARCHAR(50) NOT NULL,
                soyad VARCHAR(50) NOT NULL,
                eposta VARCHAR(100) UNIQUE NOT NULL,
                sifre_hash VARCHAR(255) NOT NULL, 
                dogum_tarihi DATE,
                cinsiyet VARCHAR(20),
                rol VARCHAR(20) NOT NULL CHECK (rol IN ('Diyetisyen', 'Danışan')),
                olusturma_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                kan_grubu VARCHAR(20),
                hastaliklar TEXT,
                boy_cm NUMERIC(5,1) 
            );
        """)

        try:
            cur.execute("ALTER TABLE kullanicilar ALTER COLUMN kan_grubu TYPE VARCHAR(20);")
        except psycopg2.Error:
            conn.rollback()
        else:
            conn.commit()

        cur.execute("ALTER TABLE kullanicilar ADD COLUMN IF NOT EXISTS boy_cm NUMERIC(5,1);")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS yemekler (
                id SERIAL PRIMARY KEY,
                yemek_adi VARCHAR(100) NOT NULL UNIQUE,
                kalori_per_birim NUMERIC(6, 2) NOT NULL DEFAULT 0,
                birim VARCHAR(20) NOT NULL DEFAULT 'gram',
                protein_100gr NUMERIC(5, 2) DEFAULT 0,
                yag_100gr NUMERIC(5, 2) DEFAULT 0,
                karbonhidrat_100gr NUMERIC(5, 2) DEFAULT 0,
                kategori VARCHAR(50) 
            );
        """)
        try:
            cur.execute("ALTER TABLE yemekler RENAME COLUMN kalori_100gr TO kalori_per_birim;")
        except psycopg2.Error:
            conn.rollback() 
        else:
            conn.commit()
        cur.execute("ALTER TABLE yemekler ADD COLUMN IF NOT EXISTS birim VARCHAR(20) NOT NULL DEFAULT 'gram';")
        

        cur.execute("""
            CREATE TABLE IF NOT EXISTS danisan_hedefleri (
                id SERIAL PRIMARY KEY,
                danisan_id INTEGER UNIQUE REFERENCES kullanicilar(id) ON DELETE CASCADE,
                baslangic_kilo NUMERIC(5, 2) NOT NULL,
                hedef_kilo NUMERIC(5, 2) NOT NULL,
                hedef_kalori_gunluk NUMERIC(5, 2),
                hedef_baslangic_tarihi DATE DEFAULT CURRENT_DATE,
                hedef_durumu VARCHAR(20) CHECK (hedef_durumu IN ('Aktif', 'Tamamlandı', 'Pasif')) DEFAULT 'Aktif',
                aktivite_seviyesi VARCHAR(50) 
            );
        """)
        cur.execute("ALTER TABLE danisan_hedefleri ADD COLUMN IF NOT EXISTS aktivite_seviyesi VARCHAR(50);")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS takip_kayitlari (
                id SERIAL PRIMARY KEY,
                danisan_id INTEGER REFERENCES kullanicilar(id) ON DELETE CASCADE,
                tuketim_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ogun_aciklama VARCHAR(255), 
                hesaplanan_kalori NUMERIC(7,2) 
            );
        """)
        cur.execute("ALTER TABLE takip_kayitlari ADD COLUMN IF NOT EXISTS ogun_aciklama VARCHAR(255);")
        cur.execute("ALTER TABLE takip_kayitlari ADD COLUMN IF NOT EXISTS hesaplanan_kalori NUMERIC(7,2);")
        try:
            cur.execute("ALTER TABLE takip_kayitlari DROP COLUMN IF EXISTS yemek_id;")
            cur.execute("ALTER TABLE takip_kayitlari DROP COLUMN IF EXISTS porsiyon_gram;")
        except psycopg2.Error:
            conn.rollback()
        else:
            conn.commit()

        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS kilo_takip (
                id SERIAL PRIMARY KEY,
                danisan_id INTEGER REFERENCES kullanicilar(id) ON DELETE CASCADE,
                tarih DATE NOT NULL DEFAULT CURRENT_DATE,
                kilo NUMERIC(5,2) NOT NULL,
                UNIQUE(danisan_id, tarih) 
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS su_takip (
                id SERIAL PRIMARY KEY,
                danisan_id INTEGER REFERENCES kullanicilar(id) ON DELETE CASCADE,
                tarih DATE NOT NULL DEFAULT CURRENT_DATE,
                miktar_ml INTEGER NOT NULL DEFAULT 0
            );
        """)

        conn.commit()
    
    except Exception as e:
        print(f"Tablo olusturma hatasi: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()


def sifre_hashle(sifre):
    byte_sifre = sifre.encode('utf-8')
    hash_lenmis_sifre = bcrypt.hashpw(byte_sifre, bcrypt.gensalt())
    return hash_lenmis_sifre.decode('utf-8')

def sifre_dogrula(girilen_sifre, hash_lenmis_sifre):
    try:
        girilen_byte = girilen_sifre.encode('utf-8')
        hash_byte = hash_lenmis_sifre.encode('utf-8')
        return bcrypt.checkpw(girilen_byte, hash_byte)
    except Exception as e:
        return False

def kullanici_kaydet(ad, soyad, eposta, sifre_duz_metin, rol='Danışan', dogum_tarihi=None, cinsiyet=None, kan_grubu=None, hastaliklar=None, boy_cm=None):
    
    hash_lenmis_sifre = sifre_hashle(sifre_duz_metin)
    
    dt_sql = None
    if dogum_tarihi:
        try:
            parcalar = dogum_tarihi.split('.')
            if len(parcalar) == 3: 
                dt_sql = f"{parcalar[2]}-{parcalar[1]}-{parcalar[0]}"
            elif len(dogum_tarihi) == 10: 
                dt_sql = dogum_tarihi
        except: 
            dt_sql = None
            
    if not cinsiyet: cinsiyet = None
    if not kan_grubu: kan_grubu = None
    if not hastaliklar: hastaliklar = None
    if not boy_cm: boy_cm = None

    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO kullanicilar 
                (ad, soyad, eposta, sifre_hash, rol, dogum_tarihi, cinsiyet, kan_grubu, hastaliklar, boy_cm)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (ad, soyad, eposta, hash_lenmis_sifre, rol, dt_sql, cinsiyet, kan_grubu, hastaliklar, boy_cm))
        
        kullanici_id = cur.fetchone()[0]
        conn.commit()
        return kullanici_id
    
    except psycopg2.IntegrityError as e:
        print(f"SQL Bütünlük Hatası (IntegrityError): {e}")
        return None
    except Exception as e:
        print(f"Genel Kayıt Hatası: {e}")
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def kullanici_giris_yap(eposta, sifre_duz_metin):
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        
        cur.execute("SELECT id, rol, sifre_hash FROM kullanicilar WHERE eposta = %s;", (eposta,))
        kullanici = cur.fetchone()
        
        if not kullanici:
            return None 

        kullanici_id, rol, hash_lenmis_sifre = kullanici
        
        if sifre_dogrula(sifre_duz_metin, hash_lenmis_sifre):
            return kullanici_id, rol 
        else:
            return None 

    except Exception as e:
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()


def kullanici_detay_getir(kullanici_id):
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        cur.execute(
            """SELECT ad, soyad, eposta, dogum_tarihi, cinsiyet, kan_grubu, hastaliklar, boy_cm 
               FROM kullanicilar WHERE id = %s;""", 
            (kullanici_id,)
        )
        kullanici = cur.fetchone()
        if kullanici:
            dt_str = str(kullanici[3] or '')
            if len(dt_str) == 10:
                dt_parcalar = dt_str.split('-')
                dt_str = f"{dt_parcalar[2]}.{dt_parcalar[1]}.{dt_parcalar[0]}"
            
            return {
                "ad": kullanici[0], "soyad": kullanici[1], "eposta": kullanici[2],
                "dogum_tarihi": dt_str, 
                "cinsiyet": kullanici[4] or '', "kan_grubu": kullanici[5] or '',
                "hastaliklar": kullanici[6] or '',
                "boy_cm": str(kullanici[7] or '') 
            }
        return None
    except Exception as e:
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def kullanici_detay_guncelle(kullanici_id, ad, soyad, dogum_tarihi, cinsiyet, kan_grubu, hastaliklar, boy_cm):
    
    dt_sql = None
    if dogum_tarihi:
        try:
            parcalar = dogum_tarihi.split('.')
            if len(parcalar) == 3: 
                dt_sql = f"{parcalar[2]}-{parcalar[1]}-{parcalar[0]}"
            elif len(dogum_tarihi) == 10: 
                dt_sql = dogum_tarihi
        except: 
            dt_sql = None
            
    if not cinsiyet: cinsiyet = None
    if not kan_grubu: kan_grubu = None
    if not hastaliklar: hastaliklar = None
    if not boy_cm: boy_cm = None

    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        cur.execute(
            """UPDATE kullanicilar SET
               ad = %s, soyad = %s, dogum_tarihi = %s, cinsiyet = %s, kan_grubu = %s, hastaliklar = %s, boy_cm = %s
               WHERE id = %s;""",
            (ad, soyad, dt_sql, cinsiyet, kan_grubu, hastaliklar, boy_cm, kullanici_id)
        )
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()


def hedef_getir(danisan_id):
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        cur.execute("""
            SELECT baslangic_kilo, hedef_kilo, aktivite_seviyesi, hedef_kalori_gunluk 
            FROM danisan_hedefleri WHERE danisan_id = %s;
            """, (danisan_id,))
        hedef = cur.fetchone()
        if hedef:
            return hedef 
        else:
            return None 
    except Exception as e:
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def danisan_hedefi_ekle_guncelle(danisan_id, baslangic_kilo, hedef_kilo, aktivite_seviyesi, hedef_durumu='Aktif', hedef_kalori_gunluk=None):
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        cur.execute("SELECT id FROM danisan_hedefleri WHERE danisan_id = %s;", (danisan_id,))
        mevcut_hedef = cur.fetchone()

        if not aktivite_seviyesi: aktivite_seviyesi = None
        
        if mevcut_hedef:
            cur.execute("""
                UPDATE danisan_hedefleri SET baslangic_kilo = %s, hedef_kilo = %s, hedef_durumu = %s, 
                aktivite_seviyesi = %s, hedef_kalori_gunluk = %s, hedef_baslangic_tarihi = CURRENT_DATE 
                WHERE danisan_id = %s;
            """, (baslangic_kilo, hedef_kilo, hedef_durumu, aktivite_seviyesi, hedef_kalori_gunluk, danisan_id))
        else:
            cur.execute("""
                INSERT INTO danisan_hedefleri (danisan_id, baslangic_kilo, hedef_kilo, hedef_durumu, aktivite_seviyesi, hedef_kalori_gunluk)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (danisan_id, baslangic_kilo, hedef_kilo, hedef_durumu, aktivite_seviyesi, hedef_kalori_gunluk))
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()


def yemek_ekle(yemek_adi, kalori_per_birim, birim='gram', kategori='Genel', protein=0, yag=0, karb=0):
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO yemekler 
                (yemek_adi, kalori_per_birim, birim, kategori, protein_100gr, yag_100gr, karbonhidrat_100gr)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (yemek_adi, kalori_per_birim, birim, kategori, protein, yag, karb))
        yemek_id = cur.fetchone()[0]
        conn.commit()
        return yemek_id
    except psycopg2.IntegrityError:
        return None
    except Exception as e:
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def yemekleri_getir():
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        cur.execute("SELECT yemek_adi, birim, kalori_per_birim FROM yemekler ORDER BY yemek_adi;")
        yemekler = cur.fetchall()
        return yemekler
    except Exception as e:
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def ogun_kaydet(danisan_id, ogun_aciklama, hesaplanan_kalori):
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO takip_kayitlari (danisan_id, ogun_aciklama, hesaplanan_kalori)
            VALUES (%s, %s, %s);
        """, (danisan_id, ogun_aciklama, hesaplanan_kalori))
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def su_kaydet(danisan_id, miktar_ml):
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        
        cur.execute("SELECT id, miktar_ml FROM su_takip WHERE danisan_id = %s AND tarih = CURRENT_DATE;", (danisan_id,))
        kayit = cur.fetchone()
        
        if kayit:
            yeni_miktar = kayit[1] + miktar_ml
            cur.execute("UPDATE su_takip SET miktar_ml = %s WHERE id = %s;", (yeni_miktar, kayit[0]))
        else:
            cur.execute("INSERT INTO su_takip (danisan_id, miktar_ml) VALUES (%s, %s);", (danisan_id, miktar_ml))
            
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def kilo_kaydet(danisan_id, kilo):
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO kilo_takip (danisan_id, kilo)
            VALUES (%s, %s)
            ON CONFLICT (danisan_id, tarih)
            DO UPDATE SET kilo = EXCLUDED.kilo;
        """, (danisan_id, kilo))
            
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_gunluk_su_ve_kilo(danisan_id):
    conn = None
    cur = None
    su_toplam = 0
    son_kilo = "N/A"
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        cur.execute("SELECT miktar_ml FROM su_takip WHERE danisan_id = %s AND tarih = CURRENT_DATE;", (danisan_id,))
        su = cur.fetchone()
        if su: su_toplam = su[0]
        
        cur.execute("SELECT kilo FROM kilo_takip WHERE danisan_id = %s ORDER BY tarih DESC LIMIT 1;", (danisan_id,))
        kilo = cur.fetchone()
        if kilo: son_kilo = kilo[0]
        
    except Exception as e:
        print(f"Veri cekme hatasi: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()
    
    return su_toplam, son_kilo

def get_kilo_gecmisi(danisan_id, gun_sayisi=30):
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        tarih_limiti = date.today() - timedelta(days=gun_sayisi)
        cur.execute("""
            SELECT tarih, kilo FROM kilo_takip 
            WHERE danisan_id = %s AND tarih >= %s
            ORDER BY tarih ASC;
        """, (danisan_id, tarih_limiti))
        
        return cur.fetchall() 
        
    except Exception as e:
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_su_gecmisi(danisan_id, gun_sayisi=30):
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        tarih_limiti = date.today() - timedelta(days=gun_sayisi)
        cur.execute("""
            SELECT tarih, miktar_ml FROM su_takip 
            WHERE danisan_id = %s AND tarih >= %s
            ORDER BY tarih ASC;
        """, (danisan_id, tarih_limiti))
        
        return cur.fetchall() 
        
    except Exception as e:
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_kalori_gecmisi(danisan_id, gun_sayisi=30):
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        tarih_limiti = date.today() - timedelta(days=gun_sayisi)
        cur.execute("""
            SELECT tuketim_zamani::DATE as tarih, SUM(hesaplanan_kalori) 
            FROM takip_kayitlari 
            WHERE danisan_id = %s AND tuketim_zamani >= %s
            GROUP BY tuketim_zamani::DATE
            ORDER BY tarih ASC;
        """, (danisan_id, tarih_limiti))
        
        return cur.fetchall() 
        
    except Exception as e:
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_yemek_onerisi(maksimum_kalori):
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        cur.execute("""
            SELECT yemek_adi, kalori_per_birim, birim FROM yemekler 
            WHERE kalori_per_birim <= %s 
            ORDER BY kalori_per_birim DESC 
            LIMIT 5;
        """, (maksimum_kalori,))
        return cur.fetchall()
    except Exception as e:
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def varsayilan_yemekleri_yukle():
    conn = None
    cur = None
    try:
        conn = baglanti_olustur()
        cur = conn.cursor()
        cur.execute("DELETE FROM yemekler WHERE yemek_adi LIKE '%(%'")
        cur.execute("DELETE FROM yemekler WHERE yemek_adi ILIKE '%prinç%' OR yemek_adi ILIKE '%pirincli%'")
        
        conn.commit()
        print("Eski/detayli ve hatali yemek verileri temizlendi.")
    except Exception as e:
        print(f"Temizlik hatasi: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

    print("Varsayılan yemek verileri yükleniyor...")

    yemek_ekle("Haşlanmış Yumurta", 78, birim='adet', kategori="Kahvaltılık", protein=6.3, yag=5.3, karb=0.6)
    yemek_ekle("Omlet", 220, birim='porsiyon', kategori="Kahvaltılık", protein=14, yag=16, karb=2)
    yemek_ekle("Beyaz Peynir", 93, birim='adet', kategori="Kahvaltılık", protein=6, yag=7, karb=1)
    yemek_ekle("Kaşar Peyniri", 71, birim='adet', kategori="Kahvaltılık", protein=5.4, yag=5.6, karb=0.5)
    yemek_ekle("Zeytin", 45, birim='porsiyon', kategori="Kahvaltılık", protein=0, yag=5, karb=1)
    yemek_ekle("Bal", 30, birim='kaşık', kategori="Kahvaltılık", protein=0, yag=0, karb=8)
    yemek_ekle("Tereyağı", 36, birim='kaşık', kategori="Kahvaltılık", protein=0, yag=4, karb=0)
    
    yemek_ekle("Beyaz Ekmek", 65, birim='dilim', kategori="Tahıl", protein=2, yag=1, karb=12)
    yemek_ekle("Tam Buğday Ekmeği", 60, birim='dilim', kategori="Tahıl", protein=3, yag=1, karb=10)
    yemek_ekle("Yulaf Ezmesi", 370, birim='gram', kategori="Tahıl", protein=13, yag=7, karb=60)
    yemek_ekle("Simit", 320, birim='adet', kategori="Tahıl", protein=10, yag=10, karb=50)

    yemek_ekle("Izgara Tavuk Göğsü", 165, birim='gram', kategori="Ana Yemek", protein=31, yag=3.6, karb=0)
    yemek_ekle("Izgara Köfte", 350, birim='porsiyon', kategori="Ana Yemek", protein=25, yag=25, karb=5)
    yemek_ekle("Izgara Somon", 208, birim='gram', kategori="Ana Yemek", protein=20, yag=13, karb=0)
    yemek_ekle("Kuru Fasulye", 280, birim='porsiyon', kategori="Ana Yemek", protein=15, yag=10, karb=30)
    yemek_ekle("Nohut Yemeği", 290, birim='porsiyon', kategori="Ana Yemek", protein=14, yag=11, karb=32)
    yemek_ekle("Mercimek Çorbası", 150, birim='porsiyon', kategori="Çorba", protein=8, yag=5, karb=18)
    yemek_ekle("Tarhana Çorbası", 180, birim='porsiyon', kategori="Çorba", protein=6, yag=6, karb=25)

    yemek_ekle("Pirinç Pilavı", 300, birim='porsiyon', kategori="Yan Lezzet", protein=5, yag=8, karb=50)
    yemek_ekle("Bulgur Pilavı", 250, birim='porsiyon', kategori="Yan Lezzet", protein=7, yag=7, karb=40)
    yemek_ekle("Makarna", 320, birim='porsiyon', kategori="Yan Lezzet", protein=10, yag=5, karb=60)

    yemek_ekle("Mevsim Salatası", 50, birim='porsiyon', kategori="Salata", protein=2, yag=0, karb=10)
    yemek_ekle("Elma", 52, birim='adet', kategori="Meyve", protein=0.3, yag=0.2, karb=14)
    yemek_ekle("Muz", 105, birim='adet', kategori="Meyve", protein=1.3, yag=0.4, karb=27)
    yemek_ekle("Portakal", 62, birim='adet', kategori="Meyve", protein=1.2, yag=0.2, karb=15)

    yemek_ekle("Yoğurt", 120, birim='adet', kategori="Süt Ürünü", protein=6, yag=6, karb=9)
    yemek_ekle("Süt", 120, birim='adet', kategori="Süt Ürünü", protein=6, yag=6, karb=9)
    yemek_ekle("Ayran", 75, birim='adet', kategori="Süt Ürünü", protein=4, yag=4, karb=6)

    yemek_ekle("Ceviz", 196, birim='porsiyon', kategori="Atıştırmalık", protein=4, yag=19, karb=4)
    yemek_ekle("Çiğ Badem", 170, birim='porsiyon', kategori="Atıştırmalık", protein=6, yag=15, karb=6)
    
    print("✅ Varsayılan yemek verileri eklendi/güncellendi.")

if __name__ == "__main__":
    tablo_olustur()
    varsayilan_yemekleri_yukle()