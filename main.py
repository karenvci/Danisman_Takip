from veritabani import tablo_olustur, kullanici_ekle, kullanicilari_goster

def uygulama_baslat():
    """Uygulamanın ana başlangıç noktası."""
    
    print("====================================")
    print("  Diyetisyen Danışman Takip Sistemi ")
    print("====================================")

    print("\n[ADIM 1] Veri Tabanı Kontrol Ediliyor...")
    tablo_olustur()
    
    print("\n[ADIM 2] Örnek Veri Girişi:")
    kullanici_ekle("Kardelen", "Avcı", "kardelen@danisan.com", "test_hash_01", "Danışan", "2001-03-15", "Kadın")
    
    print("\n[ADIM 3] Kayıtlı Kullanıcıları Görüntüleme:")
    kullanicilari_goster()
    
    print("\nUygulama Başlangıcı Tamamlandı.")

if __name__ == "__main__":
    uygulama_baslat()