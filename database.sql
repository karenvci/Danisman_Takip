CREATE TABLE kullanicilar (
    id SERIAL PRIMARY KEY,
    ad VARCHAR(50) NOT NULL,
    soyad VARCHAR(50) NOT NULL,
    eposta VARCHAR(100) UNIQUE NOT NULL,
    sifre_hash VARCHAR(255) NOT NULL,
    dogum_tarihi DATE,
    cinsiyet VARCHAR(10),
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('Diyetisyen', 'Danışan')),
    hedef_kilo NUMERIC(5, 2),
    olusturma_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE yemek_bilgileri (
    id SERIAL PRIMARY KEY,
    yemek_adi VARCHAR(100) NOT NULL UNIQUE,
    porsiyon_gram INTEGER,
    kalori_gr_cinsinden NUMERIC(5, 2) NOT NULL,
    kategori VARCHAR(50)
);