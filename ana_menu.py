import customtkinter as ctk
import re  

from veritabani import (
    tablo_olustur, 
    kullanici_kaydet, 
    kullanici_giris_yap, 
    hedef_getir, 
    danisan_hedefi_ekle_guncelle,
    yemekleri_getir, 
    ogun_kaydet,
    kullanici_detay_getir,
    kullanici_detay_guncelle,
    su_kaydet,
    kilo_kaydet,
    get_gunluk_su_ve_kilo,
    get_kilo_gecmisi,
    get_su_gecmisi,
    get_kalori_gecmisi,
    get_yemek_onerisi,
    varsayilan_yemekleri_yukle 
)

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates 
from matplotlib.dates import DateFormatter
import decimal 
from datetime import date, timedelta, datetime 
import locale 


mevcut_kullanici = {
    "id": None, "rol": None,
    "hedef_guncel_kilo": "N/A", "hedef_kilo": "N/A",
    "aktivite_seviyesi": None, "hedef_kalori": "N/A",
    "bugun_su": 0, "son_kilo": "N/A"
}
login_penceresi = None
kayit_penceresi = None
main_container = None

ACIK_YESIL_FON = "#E8F5E9"    
BEYAZ_KUTU = "#FFFFFF"       
NAVBAR_YESIL = "#A5D6A7"     
KOYU_LACIVERT = "#1A237E"   
HOVER_LACIVERT = "#10164E"  
KOYU_GRI = "#424242"        
CIKIS_BUTONU = "#D32F2F"    
GRAFIK_ARKA_PLAN = BEYAZ_KUTU  
YAZI_RENGI_KOYU = "#000000" 
YAZI_RENGI_ACIK = "#FFFFFF" 


app = ctk.CTk()
app.title("Diyetisyen Danışman Takip")
app.geometry("1100x850") 

ctk.set_appearance_mode("light") 
app.configure(fg_color=ACIK_YESIL_FON) 
ctk.set_default_color_theme("blue") 

plt.style.use('default') 
plt.rcParams['axes.facecolor'] = GRAFIK_ARKA_PLAN
plt.rcParams['figure.facecolor'] = GRAFIK_ARKA_PLAN
plt.rcParams['xtick.color'] = YAZI_RENGI_KOYU
plt.rcParams['ytick.color'] = YAZI_RENGI_KOYU
plt.rcParams['axes.labelcolor'] = YAZI_RENGI_KOYU
plt.rcParams['axes.titlecolor'] = YAZI_RENGI_KOYU

def ekrani_temizle(sadece_icerik=False):
    global main_container
    if sadece_icerik and main_container:
        for widget in main_container.winfo_children():
            widget.destroy()
    else:
        for widget in app.winfo_children():
            widget.destroy()
        main_container = None 


def header_ve_navbar_ciz():
    
    header_frame = ctk.CTkFrame(app, fg_color="transparent")
    header_frame.pack(pady=20, padx=20, fill="x") 

    ctk.CTkLabel(header_frame, text="DİYETİSYEN DANIŞMAN TAKİP", font=("Arial", 28, "bold"), text_color=YAZI_RENGI_KOYU).pack(side="left")

    auth_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    auth_frame.pack(side="right")

    if mevcut_kullanici["id"] is None:
        ctk.CTkButton(auth_frame, text="Giriş Yap", fg_color=KOYU_GRI, hover_color="#444444", text_color=YAZI_RENGI_ACIK, command=login_ekranini_ac).pack(side="left", padx=5)
        ctk.CTkButton(auth_frame, text="Üye Ol", fg_color=KOYU_GRI, hover_color="#444444", text_color=YAZI_RENGI_ACIK, command=kayit_ekranini_ac).pack(side="left", padx=5)
    else:
        ctk.CTkButton(auth_frame, text="Hesabım", fg_color=KOYU_GRI, hover_color="#444444", text_color=YAZI_RENGI_ACIK, command=hesap_sayfasini_goster).pack(side="left", padx=5)
        ctk.CTkButton(auth_frame, text="Çıkış Yap", fg_color=CIKIS_BUTONU, hover_color="#7A0000", text_color=YAZI_RENGI_ACIK, command=cikis_yap_action).pack(side="left", padx=5)

    navbar_frame = ctk.CTkFrame(app, fg_color=NAVBAR_YESIL, height=50) 
    navbar_frame.pack(pady=10, padx=20, fill="x")

    ctk.CTkButton(navbar_frame, text="ANA MENÜ", fg_color="transparent", hover_color="#81C784", text_color=YAZI_RENGI_KOYU, command=ana_sayfayi_goster).pack(side="left", padx=15)
    ctk.CTkButton(navbar_frame, text="HAKKINDA", fg_color="transparent", hover_color="#81C784", text_color=YAZI_RENGI_KOYU, command=hakkinda_sayfasini_goster).pack(side="left", padx=15)
    ctk.CTkButton(navbar_frame, text="DİYETİSYENLERİMİZ", fg_color="transparent", hover_color="#81C784", text_color=YAZI_RENGI_KOYU, command=lambda: dummy_ekran_goster("Diyetisyenlerimiz Sayfası")).pack(side="left", padx=15)
    ctk.CTkButton(navbar_frame, text="İLETİŞİM", fg_color="transparent", hover_color="#81C784", text_color=YAZI_RENGI_KOYU, command=lambda: dummy_ekran_goster("İletişim Sayfası")).pack(side="left", padx=15)
    
    ctk.CTkButton(navbar_frame, text="GRAFİKLER", fg_color="transparent", hover_color="#81C784", text_color=YAZI_RENGI_KOYU, command=grafik_sayfasini_goster).pack(side="left", padx=15)

    global main_container
    main_container = ctk.CTkFrame(app, fg_color="transparent")
    main_container.pack(pady=20, padx=20, fill="both", expand=True) 


def ana_sayfayi_goster():
    ekrani_temizle(sadece_icerik=False) 
    header_ve_navbar_ciz() 
    ana_sayfa_icerigi_ciz(main_container) 

def ana_sayfa_icerigi_ciz(master_frame):
    
    center_frame = ctk.CTkFrame(master_frame, fg_color="transparent")
    center_frame.pack(expand=True, anchor="center") 
 
    ctk.CTkLabel(center_frame, text="Ne Yapmayı Planlıyorsun?", font=("Arial", 32, "bold"), text_color=YAZI_RENGI_KOYU).pack(pady=(0, 20)) 

    button_container = ctk.CTkFrame(center_frame, fg_color="transparent")
    button_container.pack(pady=10, padx=10) 

    global KOYU_LACIVERT, HOVER_LACIVERT
    
    ctk.CTkButton(button_container, text="KİLO ALMA", width=200, height=50, font=("Arial", 18, "bold"),
                    fg_color=KOYU_LACIVERT, hover_color=HOVER_LACIVERT, text_color=YAZI_RENGI_ACIK,
                    command=lambda: hedef_sec_action("Kilo Alma")).pack(side="left", padx=10, pady=15)
    
    ctk.CTkButton(button_container, text="KİLO VERME", width=200, height=50, font=("Arial", 18, "bold"),
                    fg_color=KOYU_LACIVERT, hover_color=HOVER_LACIVERT, text_color=YAZI_RENGI_ACIK,
                    command=lambda: hedef_sec_action("Kilo Verme")).pack(side="left", padx=10, pady=15)
    
    ctk.CTkButton(button_container, text="FORMU KORUMA", width=200, height=50, font=("Arial", 18, "bold"),
                    fg_color=KOYU_LACIVERT, hover_color=HOVER_LACIVERT, text_color=YAZI_RENGI_ACIK,
                    command=lambda: hedef_sec_action("Formu Koruma")).pack(side="left", padx=10, pady=15)
    

def hedef_sec_action(secim):
    if mevcut_kullanici["id"] is None:
        login_ekranini_ac()
    else:
        hedef = hedef_getir(mevcut_kullanici["id"])
        
        if hedef:
            baslangic, hedef_kg, aktivite, hedef_kalori = hedef
            mevcut_hedef_tipi = ""
            
            try: 
                if float(hedef_kg) > float(baslangic): mevcut_hedef_tipi = "Kilo Alma"
                elif float(hedef_kg) < float(baslangic): mevcut_hedef_tipi = "Kilo Verme"
                else: mevcut_hedef_tipi = "Formu Koruma"
            except: pass 
            
            if secim == mevcut_hedef_tipi:
                ekrani_temizle(sadece_icerik=True)
                hedef_onay_goster(main_container, secim, hedef)
            else:
                ekrani_temizle(sadece_icerik=True)
                form_goster(main_container, secim) 
        else:
            ekrani_temizle(sadece_icerik=True)
            form_goster(main_container, secim)


def hedef_onay_goster(master_frame, secim, hedef):
    
    guncel_kilo = mevcut_kullanici.get("hedef_guncel_kilo", hedef[0])
    hedef_kilo = mevcut_kullanici.get("hedef_kilo", hedef[1])
    
    content_box = ctk.CTkFrame(master_frame, fg_color=BEYAZ_KUTU)
    content_box.pack(pady=20, padx=20, expand=True, fill="both") 

    ctk.CTkLabel(content_box, text=f"Zaten Bir '{secim}' Hedefiniz Var", font=("Arial", 28), text_color=YAZI_RENGI_KOYU).pack(pady=20, padx=50)
    ctk.CTkLabel(content_box, text=f"Mevcut hedefiniz: {hedef_kilo} kg", font=("Arial", 18), text_color=YAZI_RENGI_KOYU).pack(pady=10)
    ctk.CTkLabel(content_box, text="Ne yapmak istiyorsunuz?", font=("Arial", 18), text_color=YAZI_RENGI_KOYU).pack(pady=10)

    ctk.CTkButton(content_box, text="Ana Ekranıma Git (Dashboard)", width=300, height=50, 
                    command=lambda: dashboard_goster()).pack(pady=15)
                    
    ctk.CTkButton(content_box, text="Yeni Hedef Belirle (Değiştir)", width=300, height=50,
                    command=lambda: yeni_hedef_belirle(secim)).pack(pady=15)
                    
    ctk.CTkButton(content_box, text="İptal (Ana Sayfaya Dön)", width=300, height=50, fg_color="transparent", hover_color="#E0E0E0", text_color=YAZI_RENGI_KOYU,
                    command=ana_sayfayi_goster).pack(pady=15, padx=50)

def yeni_hedef_belirle(secim):
    ekrani_temizle(sadece_icerik=True)
    form_goster(main_container, secim)

def form_goster(master_frame, secim):
    
    content_box = ctk.CTkFrame(master_frame, fg_color=BEYAZ_KUTU)
    content_box.pack(pady=20, padx=20, expand=True, fill="both")

    def hedefi_kaydet_action_GERCEK():
        guncel_kilo = kilo_entry.get()
        hedef_kilo = hedef_entry.get()
        aktivite_seviyesi = aktivite_combo.get() 
        
        if not guncel_kilo or not hedef_kilo:
            mesaj_labeli.configure(text="Kilo alanlari bos birakilamaz.", text_color="#D90000") 
            return
        if not aktivite_seviyesi or aktivite_seviyesi == "Seçiniz...": 
            mesaj_labeli.configure(text="Lutfen aktivite seviyenizi secin.", text_color="#D90000")
            return
        
        danisan_id = mevcut_kullanici.get("id")
        
        hesaplanan_kalori = 2000
        kullanici_detay = kullanici_detay_getir(danisan_id)
        if kullanici_detay:
            try:
                boy = float(kullanici_detay.get("boy_cm") or 170)
                dt = kullanici_detay.get("dogum_tarihi")
                yas = 30
                if dt:
                    dy = int(dt.split('.')[-1])
                    yas = date.today().year - dy
                
                kilo = float(guncel_kilo)
                cinsiyet = kullanici_detay.get("cinsiyet")
                
                bmr = 0
                if cinsiyet == "Erkek":
                    bmr = 66.5 + (13.75 * kilo) + (5.003 * boy) - (6.755 * yas)
                else:
                    bmr = 655.1 + (9.563 * kilo) + (1.850 * boy) - (4.676 * yas)
                
                carpan = 1.2
                if "Az Aktif" in aktivite_seviyesi: carpan = 1.375
                elif "Orta Aktif" in aktivite_seviyesi: carpan = 1.55
                elif "Çok Aktif" in aktivite_seviyesi: carpan = 1.725
                
                tdee = bmr * carpan
                
                if secim == "Kilo Verme":
                    hesaplanan_kalori = tdee - 500
                elif secim == "Kilo Alma":
                    hesaplanan_kalori = tdee + 500
                else:
                    hesaplanan_kalori = tdee
                    
            except Exception as e:
                print(f"Kalori hesaplama hatasi: {e}")
                hesaplanan_kalori = 2000

        try:
            basarili = danisan_hedefi_ekle_guncelle(
                danisan_id=danisan_id,
                baslangic_kilo=float(guncel_kilo),
                hedef_kilo=float(hedef_kilo),
                aktivite_seviyesi=aktivite_seviyesi,
                hedef_kalori_gunluk=hesaplanan_kalori
            )
        except Exception as e:
            basarili = False
        
        if basarili:
            mevcut_kullanici["hedef_guncel_kilo"] = guncel_kilo
            mevcut_kullanici["hedef_kilo"] = hedef_kilo
            mevcut_kullanici["aktivite_seviyesi"] = aktivite_seviyesi
            mevcut_kullanici["hedef_kalori"] = f"{hesaplanan_kalori:.0f}"
            
            dashboard_goster() 
        else:
            mesaj_labeli.configure(text="Hata: Hedef veritabanina kaydedilemedi.", text_color="#D90000")

    ctk.CTkLabel(content_box, text=f"{secim} Formu", font=("Arial", 28), text_color=YAZI_RENGI_KOYU).pack(pady=20)
    
    ctk.CTkLabel(content_box, text="Guncel Kilo (kg):", text_color=YAZI_RENGI_KOYU).pack(pady=(10,0))
    kilo_entry = ctk.CTkEntry(content_box, placeholder_text="Orn: 85")
    kilo_entry.pack(pady=5)
    
    ctk.CTkLabel(content_box, text="Hedef Kilo (kg):", text_color=YAZI_RENGI_KOYU).pack(pady=(10,0))
    hedef_entry = ctk.CTkEntry(content_box, placeholder_text="Orn: 75")
    hedef_entry.pack(pady=5)
    
    ctk.CTkLabel(content_box, text="Aktivite Seviyesi:", text_color=YAZI_RENGI_KOYU).pack(pady=(10,0))
    aktivite_combo = ctk.CTkComboBox(content_box, values=[
        "Seçiniz...", 
        "Hareketsiz (Ofis işi)", 
        "Az Aktif (Haftada 1-3 gün hafif egzersiz)", 
        "Orta Aktif (Haftada 3-5 gün orta egzersiz)", 
        "Çok Aktif (Haftada 6-7 gün ağır egzersiz)"
    ], width=300)
    aktivite_combo.pack(pady=5)
    aktivite_combo.set("Seçiniz...")
    
    mesaj_labeli = ctk.CTkLabel(content_box, text="", font=("Arial", 12), text_color="red")
    mesaj_labeli.pack(pady=10)
    
    kaydet_butonu = ctk.CTkButton(content_box, text="Programımı Oluştur", command=hedefi_kaydet_action_GERCEK, width=200, height=40)
    kaydet_butonu.pack(pady=20)
    
    ctk.CTkButton(content_box, text="Geri Dön (Ana Sayfa)", fg_color="transparent", hover_color="#E0E0E0", text_color=YAZI_RENGI_KOYU,
                  command=ana_sayfayi_goster).pack(pady=10)


def dashboard_goster():
    ekrani_temizle(sadece_icerik=False) 
    header_ve_navbar_ciz() 
    dashboard_icerigi_ciz(main_container)


def dashboard_icerigi_ciz(master_frame):
    
    danisan_id = mevcut_kullanici["id"]
    su_toplam, son_kilo = get_gunluk_su_ve_kilo(danisan_id)
    
    bugun_kalori_data = get_kalori_gecmisi(danisan_id, gun_sayisi=1)
    toplam_kalori = 0
    if bugun_kalori_data:
        son_tarih, son_deger = bugun_kalori_data[-1]
        if son_tarih == date.today():
            toplam_kalori = son_deger

    mevcut_kullanici["bugun_su"] = su_toplam
    mevcut_kullanici["son_kilo"] = str(son_kilo) if son_kilo else "N/A"
    
    guncel_kilo = mevcut_kullanici.get("hedef_guncel_kilo", "N/A")
    hedef_kilo = mevcut_kullanici.get("hedef_kilo", "N/A")
    hedef_kalori_str = mevcut_kullanici.get("hedef_kalori", "2000")
    
    def ogun_ekle_action():
        ekrani_temizle(sadece_icerik=True)
        ogun_ekle_ekranini_goster(main_container)

    chat_box_frame = None

    def toggle_chat():
        nonlocal chat_box_frame
        if chat_box_frame is not None:
            chat_box_frame.destroy()
            chat_box_frame = None
            return

        chat_box_frame = ctk.CTkFrame(master_frame, width=650, height=650, corner_radius=15, fg_color=BEYAZ_KUTU, border_width=2, border_color="#FF9800")
        chat_box_frame.place(relx=0.98, rely=0.88, anchor="se") 

        header = ctk.CTkFrame(chat_box_frame, height=40, corner_radius=10, fg_color="#FF9800")
        header.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(header, text="Diyetisyen Asistanı", text_color="white", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(header, text="X", width=30, fg_color="transparent", text_color="white", hover_color="#F57C00", command=toggle_chat).pack(side="right", padx=5)

        messages_area = ctk.CTkScrollableFrame(chat_box_frame, fg_color="transparent", width=610)
        messages_area.pack(fill="both", expand=True, padx=5, pady=5)

        def add_message(text, sender="bot"):
            bubble_color = "#E0E0E0" if sender == "bot" else "#DCF8C6" 
            align = "w" if sender == "bot" else "e"
            text_color = "black"
            
            msg_frame = ctk.CTkFrame(messages_area, fg_color="transparent")
            msg_frame.pack(fill="x", pady=2)

            label = ctk.CTkLabel(msg_frame, text=text, fg_color=bubble_color, text_color=text_color, corner_radius=10, wraplength=580, padx=10, pady=5, justify="left")
            label.pack(anchor=align, padx=5)

        try:
            hedef_val = float(hedef_kalori_str)
            alinan_val = float(toplam_kalori)
            kalan = hedef_val - alinan_val
            
            if kalan > 0:
                initial_msg = f"Merhaba! Bugün hedefine ulaşmak için {kalan:.0f} Kcal daha alman gerekiyor. Ne yemek istersin?"
            else:
                initial_msg = f"Dikkat! Bugün hedefini {abs(kalan):.0f} Kcal aştın. Yarın daha dengeli beslenmeye çalışmalısın."
            
            add_message(initial_msg, "bot")
        except:
            add_message("Merhaba! Size nasıl yardımcı olabilirim?", "bot")

        quick_frame = ctk.CTkScrollableFrame(chat_box_frame, fg_color="transparent", height=40, orientation="horizontal")
        quick_frame.pack(fill="x", padx=5, pady=(0, 5))

        def send_message_with_text(text=None):
            user_text = text if text else entry.get()
            if not user_text: return
            
            add_message(user_text, "user")
            entry.delete(0, 'end')
            
            app.after(500, lambda: respond(user_text))

        btn_yemek = ctk.CTkButton(quick_frame, text="Yemek Önerisi", width=100, height=25, fg_color="#4CAF50", hover_color="#43A047", font=("Arial", 11), command=lambda: send_message_with_text("Yemek Önerisi"))
        btn_yemek.pack(side="left", padx=2)
        
        btn_kalori = ctk.CTkButton(quick_frame, text="Kalori Durumum", width=100, height=25, fg_color="#2196F3", hover_color="#1E88E5", font=("Arial", 11), command=lambda: send_message_with_text("Kalori Durumum"))
        btn_kalori.pack(side="left", padx=2)
        
        btn_su = ctk.CTkButton(quick_frame, text="Su Durumum", width=90, height=25, fg_color="#03A9F4", hover_color="#039BE5", font=("Arial", 11), command=lambda: send_message_with_text("Su Durumum"))
        btn_su.pack(side="left", padx=2)

        input_frame = ctk.CTkFrame(chat_box_frame, height=50, fg_color="transparent")
        input_frame.pack(fill="x", padx=5, pady=5)
        
        entry = ctk.CTkEntry(input_frame, placeholder_text="Mesajınızı yazın...", height=40)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def respond(user_text):
            user_text = user_text.lower()
            resp = ""

            try:
                hedef_val = float(hedef_kalori_str)
                alinan_val = float(toplam_kalori)
                kalan_kalori = hedef_val - alinan_val
                
                su_tuketimi = mevcut_kullanici['bugun_su']
                su_hedefi = 2500 
                kalan_su = su_hedefi - su_tuketimi
            except:
                hedef_val, alinan_val, kalan_kalori = 2000, 0, 2000
                su_tuketimi, kalan_su = 0, 2500

            if "öneri" in user_text or "ne ye" in user_text or "yemek" in user_text:
                if kalan_kalori > 0:
                    oneriler = get_yemek_onerisi(kalan_kalori)
                    if oneriler:
                        resp = "Şunları yiyebilirsin:\n" + "\n".join([f"- {y[0]} ({y[1]} kcal/{y[2]})" for y in oneriler])
                    else:
                        resp = "Bu kaloriye uygun tam bir öneri bulamadım, hafif atıştırmalıklar (meyve, kuruyemiş) tercih et."
                else:
                    resp = "Bugünlük kalori limitini doldurdun. Eğer çok açsan salatalık, yeşillik gibi düşük kalorili besinler tüketmelisin."
            
            elif "kalori" in user_text:
                resp = f"Günlük Hedef: {hedef_val:.0f} Kcal\nAlınan: {alinan_val:.0f} Kcal\n"
                if kalan_kalori > 0:
                    resp += f"Kalan İhtiyaç: {kalan_kalori:.0f} Kcal"
                else:
                    resp += f"Aşılan Miktar: {abs(kalan_kalori):.0f} Kcal"
            
            elif "su" in user_text:
                resp = f"Bugün toplam {su_tuketimi} ml su içtin.\n"
                if kalan_su > 0:
                    resp += f"Hedefine ulaşmak için {kalan_su} ml daha içmelisin."
                else:
                    resp += "Harika! Günlük su hedefini tamamladın."
            
            elif "merhaba" in user_text:
                resp = "Merhaba! Sağlıklı bir gün dilerim. Nasıl yardımcı olabilirim?"
            else:
                resp = "Bunu tam anlayamadım. Lütfen 'Yemek önerisi', 'Kalori' veya 'Su' ile ilgili bir şeyler sor."
            
            add_message(resp, "bot")

        send_btn = ctk.CTkButton(input_frame, text="Gönder", width=60, height=40, fg_color="#FF9800", hover_color="#F57C00", command=lambda: send_message_with_text())
        send_btn.pack(side="right")
        
        entry.bind("<Return>", lambda event: send_message_with_text())


    def su_ekle_action_GERCEK(miktar):
        basarili = su_kaydet(danisan_id, miktar)
        if basarili:
            dashboard_goster() 
        else:
            mesaj_labeli.configure(text="Hata: Su kaydedilemedi.", text_color="red")
            
    def kilo_kaydet_action_GERCEK():
        girilen_kilo_str = kilo_entry.get()
        if not girilen_kilo_str:
            mesaj_labeli_kilo.configure(text="Lutfen kilonuzu girin.", text_color="red")
            return
        try:
            girilen_kilo = float(girilen_kilo_str)
            basarili = kilo_kaydet(danisan_id, girilen_kilo)
            if basarili:
                mevcut_kullanici["son_kilo"] = girilen_kilo
                son_kilo_label.configure(text=f"Kaydedilen Son Kilo: {girilen_kilo} kg")
                mesaj_labeli_kilo.configure(text="Kilo basariyla kaydedildi!", text_color="green")
                kilo_entry.delete(0, 'end')
                dashboard_goster()
            else:
                mesaj_labeli_kilo.configure(text="Hata: Kilo kaydedilemedi.", text_color="red")
        except ValueError:
            mesaj_labeli_kilo.configure(text="Lutfen gecerli bir sayi girin.", text_color="red")

    
    sol_frame = ctk.CTkFrame(master_frame, fg_color=BEYAZ_KUTU)
    sol_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

    ctk.CTkLabel(sol_frame, text="Danışan Ana Ekranı", font=("Arial", 28), text_color=YAZI_RENGI_KOYU).pack(pady=20)
    
    hedef_frame = ctk.CTkFrame(sol_frame, fg_color="#F1F8E9") 
    hedef_frame.pack(pady=10, padx=20, fill="x")
    ctk.CTkLabel(hedef_frame, text=f"Mevcut Kilo: {guncel_kilo} kg", font=("Arial", 16), text_color=YAZI_RENGI_KOYU).pack(pady=5)
    ctk.CTkLabel(hedef_frame, text=f"Hedef Kilo: {hedef_kilo} kg", font=("Arial", 16), text_color=YAZI_RENGI_KOYU).pack(pady=5)
    
    kalori_frame = ctk.CTkFrame(sol_frame, fg_color="#F1F8E9") 
    kalori_frame.pack(pady=10, padx=20, fill="x")
    ctk.CTkLabel(kalori_frame, text="Bugünkü Kalori Durumu", font=("Arial", 14), text_color=YAZI_RENGI_KOYU).pack(pady=5)
    ctk.CTkLabel(kalori_frame, text=f"Alınan: {toplam_kalori:.0f} / {hedef_kalori_str} Kcal", font=("Arial", 20, "bold"), text_color=YAZI_RENGI_KOYU).pack(pady=5)
    
    ctk.CTkButton(sol_frame, text="Öğün Ekle", width=150, height=40, command=ogun_ekle_action).pack(pady=10)
    
    sag_frame = ctk.CTkFrame(master_frame, fg_color=BEYAZ_KUTU) 
    sag_frame.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
    
    ctk.CTkLabel(sag_frame, text="Su Takibi", font=("Arial", 20), text_color=YAZI_RENGI_KOYU).pack(pady=20)
    ctk.CTkLabel(sag_frame, text=f"Bugün Tüketilen: {mevcut_kullanici['bugun_su']} ml", font=("Arial", 16), text_color=YAZI_RENGI_KOYU).pack(pady=10)
    
    su_buton_frame = ctk.CTkFrame(sag_frame, fg_color="transparent")
    su_buton_frame.pack(pady=10)
    ctk.CTkButton(su_buton_frame, text="+ 1 Bardak (200ml)", command=lambda: su_ekle_action_GERCEK(200)).pack(fill="x", pady=5)
    ctk.CTkButton(su_buton_frame, text="+ 1 Şişe (500ml)", command=lambda: su_ekle_action_GERCEK(500)).pack(fill="x", pady=5)
    mesaj_labeli = ctk.CTkLabel(su_buton_frame, text="", font=("Arial", 12)) 
    mesaj_labeli.pack(pady=10)

    ctk.CTkLabel(sag_frame, text="Kilo Takibi", font=("Arial", 20), text_color=YAZI_RENGI_KOYU).pack(pady=(30, 10))
    son_kilo_label = ctk.CTkLabel(sag_frame, text=f"Kaydedilen Son Kilo: {mevcut_kullanici['son_kilo']} kg", font=("Arial", 16), text_color=YAZI_RENGI_KOYU)
    son_kilo_label.pack(pady=10)
    
    ctk.CTkLabel(sag_frame, text="Bugünkü Kilonuzu Kaydedin:", font=("Arial", 12), text_color=YAZI_RENGI_KOYU).pack(pady=(10,0))
    kilo_entry = ctk.CTkEntry(sag_frame, placeholder_text="Orn: 84.5", width=150)
    kilo_entry.pack(pady=10)
    ctk.CTkButton(sag_frame, text="Kilomu Kaydet", command=kilo_kaydet_action_GERCEK).pack(pady=10)

    mesaj_labeli_kilo = ctk.CTkLabel(sag_frame, text="", font=("Arial", 12)) 
    mesaj_labeli_kilo.pack(pady=10)

    asistan_btn = ctk.CTkButton(master_frame, text="💬 Diyetisyene Sor", width=200, height=50, 
                                fg_color="#FF9800", hover_color="#F57C00", 
                                font=("Arial", 16, "bold"), corner_radius=25,
                                command=toggle_chat)
    asistan_btn.place(relx=0.98, rely=0.98, anchor="se")


def ogun_ekle_ekranini_goster(master_frame):
    
    ekrani_temizle(sadece_icerik=True)

    ham_yemek_listesi = yemekleri_getir()

    yemek_listesi_data = []
    gorulen_yemekler = set()
    
    if ham_yemek_listesi:
        
        for yemek in ham_yemek_listesi:

            temiz_ad = re.sub(r'\s*\(.*?\)', '', str(yemek[0])).strip()
            ad_key = temiz_ad.lower()
            
            if ad_key and ad_key not in gorulen_yemekler:
                gorulen_yemekler.add(ad_key)
                yeni_veri = (temiz_ad, yemek[1], yemek[2])
                yemek_listesi_data.append(yeni_veri)
    
    yemek_listesi_data.sort(key=lambda x: x[0])
 
    if not yemek_listesi_data: 
        yemek_adlari = ["Veritabaninda yemek bulunamadi"]
    else:
        yemek_adlari = [yemek[0] for yemek in yemek_listesi_data]

    def on_yemek_secimi(secilen_ad):
        secilen_yemek_data = next(
            (yemek for yemek in yemek_listesi_data if yemek[0] == secilen_ad), 
            None
        )
        if secilen_yemek_data:
            (yemek_adi, birim, kalori_per_birim) = secilen_yemek_data
            if birim == 'adet':
                miktar_label.configure(text="Miktar (Adet olarak):")
            elif birim == 'dilim':
                miktar_label.configure(text="Miktar (Dilim olarak):")
            else: 
                miktar_label.configure(text="Miktar (Gram olarak):")
        else:
            miktar_label.configure(text="Miktar:")

    def ogunu_kaydet_action_GERCEK():
        secilen_yemek_ad = yemek_listesi_combobox.get()
        girilen_miktar_str = miktar_entry.get()
        danisan_id = mevcut_kullanici.get("id")
        
        if not secilen_yemek_ad or not girilen_miktar_str or not danisan_id or secilen_yemek_ad == "Veritabaninda yemek bulunamadi":
            mesaj_labeli.configure(text="Lutfen bir yemek secin ve miktar girin.", text_color="red")
            return
        try:
            girilen_miktar = float(girilen_miktar_str)
        except ValueError:
            mesaj_labeli.configure(text="Lutfen miktar alanina sayi girin.", text_color="red")
            return

        secilen_yemek_data = next(
            (yemek for yemek in yemek_listesi_data if yemek[0] == secilen_yemek_ad), 
            None
        )
        if not secilen_yemek_data:
            mesaj_labeli.configure(text="Hata: Secilen yemek verisi bulunamadi.", text_color="red")
            return
            
        (yemek_adi, birim, kalori_per_birim) = secilen_yemek_data
        
        kalori_float = float(kalori_per_birim)
        
        hesaplanan_kalori = 0
        ogun_aciklama = ""
        
        if birim == 'adet':
            hesaplanan_kalori = girilen_miktar * kalori_float
            ogun_aciklama = f"{yemek_adi} ({girilen_miktar} adet)"
        elif birim == 'dilim':
            hesaplanan_kalori = girilen_miktar * kalori_float
            ogun_aciklama = f"{yemek_adi} ({girilen_miktar} dilim)"
        else: 
            hesaplanan_kalori = (girilen_miktar / 100) * kalori_float
            ogun_aciklama = f"{yemek_adi} ({girilen_miktar} gram)"

        basarili = ogun_kaydet(danisan_id, ogun_aciklama, hesaplanan_kalori)
        
        if basarili:
            mesaj_labeli.configure(text=f"{ogun_aciklama} ({hesaplanan_kalori:.0f} Kcal) eklendi.", text_color="green")
            miktar_entry.delete(0, 'end')
            yemek_listesi_combobox.set("")
            miktar_label.configure(text="Miktar:")
        else:
            mesaj_labeli.configure(text="Hata: Ogun kaydedilemedi.", text_color="red")

    content_box = ctk.CTkFrame(master_frame, fg_color=BEYAZ_KUTU)
    content_box.pack(pady=20, padx=20, expand=True, fill="both")
    
    ctk.CTkLabel(content_box, text="Öğün Ekle", font=("Arial", 28), text_color=YAZI_RENGI_KOYU).pack(pady=20)
    
    ctk.CTkLabel(content_box, text="Yemek Seçin:", font=("Arial", 16), text_color=YAZI_RENGI_KOYU).pack(pady=10)
    yemek_listesi_combobox = ctk.CTkComboBox(
        content_box, 
        values=yemek_adlari, 
        width=300,
        command=on_yemek_secimi 
    )
    yemek_listesi_combobox.pack(pady=10)
    
    miktar_label = ctk.CTkLabel(content_box, text="Miktar:", font=("Arial", 16), text_color=YAZI_RENGI_KOYU)
    miktar_label.pack(pady=10)
    
    miktar_entry = ctk.CTkEntry(content_box, placeholder_text="Orn: 1.5 (adet) veya 150 (gram)", width=200)
    miktar_entry.pack(pady=10)
    
    ctk.CTkButton(content_box, text="Öğünü Kaydet", width=200, height=40, command=ogunu_kaydet_action_GERCEK).pack(pady=20)
    mesaj_labeli = ctk.CTkLabel(content_box, text="", font=("Arial", 12))
    mesaj_labeli.pack(pady=10)
    ctk.CTkButton(content_box, text="Geri Dön (Ana Ekran)", fg_color="transparent", hover_color="#E0E0E0", text_color=YAZI_RENGI_KOYU,
                  command=lambda: dashboard_goster()).pack(pady=20)


def hesap_sayfasini_goster():
    kullanici_id = mevcut_kullanici.get("id")
    if not kullanici_id:
        login_ekranini_ac() 
        return

    ekrani_temizle(sadece_icerik=False) 
    header_ve_navbar_ciz() 
    hesap_icerigi_ciz(main_container, kullanici_id) 

def hesap_icerigi_ciz(master_frame, kullanici_id):
    
    mevcut_bilgiler = kullanici_detay_getir(kullanici_id)
    if not mevcut_bilgiler:
        ctk.CTkLabel(master_frame, text="Hata: Kullanici detaylari cekilemedi.", text_color="red").pack()
        return

    def guncelle_action_GERCEK():
        yeni_ad = ad_entry.get()
        yeni_soyad = soyad_entry.get()
        yeni_dt = dt_entry.get()
        yeni_cinsiyet = cinsiyet_combo.get()
        yeni_kan_grubu = kan_combo.get()
        yeni_hastaliklar = hastalik_text.get("1.0", "end-1c")
        yeni_boy_cm = boy_entry.get() 

        if not yeni_ad or not yeni_soyad:
            mesaj_labeli.configure(text="Ad ve Soyad zorunludur.", text_color="red")
            return
        if yeni_dt and len(yeni_dt) != 10 and len(yeni_dt) != 0: 
             mesaj_labeli.configure(text="Dogum Tarihi formatı GG.AA.YYYY olmalı.", text_color="red")
             return

        basarili = kullanici_detay_guncelle(
            kullanici_id=kullanici_id,
            ad=yeni_ad, soyad=yeni_soyad,
            dogum_tarihi=yeni_dt if yeni_dt else None,
            cinsiyet=yeni_cinsiyet if yeni_cinsiyet != "Seçiniz..." else None,
            kan_grubu=yeni_kan_grubu if yeni_kan_grubu != "Seçiniz..." else None,
            hastaliklar=yeni_hastaliklar,
            boy_cm=yeni_boy_cm if yeni_boy_cm else None 
        )

        if basarili:
            mesaj_labeli.configure(text="Bilgiler basariyla guncellendi!", text_color="green")
        else:
            mesaj_labeli.configure(text="Hata: Guncelleme basarisiz.", text_color="red")

    content_box = ctk.CTkScrollableFrame(master_frame, fg_color=BEYAZ_KUTU)
    content_box.pack(pady=20, padx=20, expand=True, fill="both")

    ctk.CTkLabel(content_box, text="Hesap Bilgileri", font=("Arial", 28), text_color=YAZI_RENGI_KOYU).pack(pady=20)
    
    ctk.CTkLabel(content_box, text="Ad:", text_color=YAZI_RENGI_KOYU).pack(anchor="w", padx=50)
    ad_entry = ctk.CTkEntry(content_box, width=340)
    ad_entry.pack(pady=(0,10), padx=50)
    ad_entry.insert(0, mevcut_bilgiler.get("ad")) 

    ctk.CTkLabel(content_box, text="Soyad:", text_color=YAZI_RENGI_KOYU).pack(anchor="w", padx=50)
    soyad_entry = ctk.CTkEntry(content_box, width=340)
    soyad_entry.pack(pady=(0,10), padx=50)
    soyad_entry.insert(0, mevcut_bilgiler.get("soyad")) 
    
    ctk.CTkLabel(content_box, text="E-posta (Değiştirilemez):", text_color=YAZI_RENGI_KOYU).pack(anchor="w", padx=50)
    eposta_entry = ctk.CTkEntry(content_box, width=340, fg_color="#E0E0E0", text_color=YAZI_RENGI_KOYU) 
    eposta_entry.pack(pady=(0,10), padx=50)
    eposta_entry.insert(0, mevcut_bilgiler.get("eposta")) 
    eposta_entry.configure(state="disabled") 
    
    ctk.CTkLabel(content_box, text="Doğum Tarihi:", text_color=YAZI_RENGI_KOYU).pack(anchor="w", padx=50)
    dt_entry = ctk.CTkEntry(content_box, placeholder_text="GG.AA.YYYY", width=340)
    dt_entry.pack(pady=(0,10), padx=50)
    dt_entry.insert(0, mevcut_bilgiler.get("dogum_tarihi"))
    
    ctk.CTkLabel(content_box, text="Boy (cm):", text_color=YAZI_RENGI_KOYU).pack(anchor="w", padx=50)
    boy_entry = ctk.CTkEntry(content_box, placeholder_text="Orn: 175.5", width=340)
    boy_entry.pack(pady=(0,10), padx=50)
    boy_entry.insert(0, mevcut_bilgiler.get("boy_cm")) 
    
    ctk.CTkLabel(content_box, text="Cinsiyet:", text_color=YAZI_RENGI_KOYU).pack(anchor="w", padx=50)
    cinsiyet_combo = ctk.CTkComboBox(content_box, values=["Seçiniz...", "Erkek", "Kadın", "Belirtmek istemiyorum"], width=340)
    cinsiyet_combo.pack(pady=(0,10), padx=50)
    cinsiyet_combo.set(mevcut_bilgiler.get("cinsiyet") or "Seçiniz...") 
    
    ctk.CTkLabel(content_box, text="Kan Grubu:", text_color=YAZI_RENGI_KOYU).pack(padx=50, anchor="w")
    kan_combo = ctk.CTkComboBox(content_box, values=["Seçiniz...", "A+", "A-", "B+", "B-", "AB+", "AB-", "0+", "0-", "Bilmiyorum"], width=340)
    kan_combo.pack(pady=(0,10), padx=50)
    kan_combo.set(mevcut_bilgiler.get("kan_grubu") or "Seçiniz...") 
    
    ctk.CTkLabel(content_box, text="Bilinen Hastalıklar (varsa):").pack(padx=30, anchor="w")
    hastalik_text = ctk.CTkTextbox(content_box, width=340, height=100)
    hastalik_text.pack(pady=(0,10), padx=30)
    hastalik_text.insert("1.0", mevcut_bilgiler.get("hastaliklar")) 

    mesaj_labeli = ctk.CTkLabel(content_box, text="", font=("Arial", 12))
    mesaj_labeli.pack(pady=10)
    
    button_frame = ctk.CTkFrame(content_box, fg_color="transparent")
    button_frame.pack(pady=10)

    guncelle_butonu = ctk.CTkButton(button_frame, text="Güncelle", width=150, height=40, 
                                   command=guncelle_action_GERCEK,
                                   fg_color=KOYU_LACIVERT, hover_color=HOVER_LACIVERT, text_color=YAZI_RENGI_ACIK)
    guncelle_butonu.pack(side="left", padx=5)
    
    kaydet_butonu = ctk.CTkButton(button_frame, text="Kaydet", width=150, height=40, 
                                 command=guncelle_action_GERCEK,
                                 fg_color=KOYU_LACIVERT, hover_color=HOVER_LACIVERT, text_color=YAZI_RENGI_ACIK)
    kaydet_butonu.pack(side="left", padx=5)

    ctk.CTkButton(content_box, text="Geri Dön (Ana Sayfa)", fg_color="transparent", hover_color="#E0E0E0", text_color=YAZI_RENGI_KOYU,
                  command=ana_sayfayi_goster).pack(pady=(20,10))


def diyetisyen_paneli_goster():
    ekrani_temizle(sadece_icerik=False) 
    header_ve_navbar_ciz() 
    diyetisyen_paneli_icerigi_ciz(main_container)

def diyetisyen_paneli_icerigi_ciz(master_frame):
    TEST_DANISANLAR = ["İbrahim Furkan Hasanoğlu", "Kardelen Avcı", "Fatma Kırıcı"]
    
    def danisan_sec_action(secilen_ad):
        print(f"Diyetisyen {secilen_ad} adli danisani secti.")
        dummy_ekran_goster(f"{secilen_ad} Detayları (TODO)")

    ctk.CTkLabel(master_frame, text="Diyetisyen Paneli", font=("Arial", 28), text_color=YAZI_RENGI_KOYU).pack(pady=20)
    ctk.CTkLabel(master_frame, text="Danışanlarım (Test Listesi)", font=("Arial", 16), text_color=YAZI_RENGI_KOYU).pack(pady=5)
    danisan_listesi_frame = ctk.CTkScrollableFrame(master_frame, width=400, height=300)
    danisan_listesi_frame.pack(pady=10)
    for danisan in TEST_DANISANLAR:
        ctk.CTkButton(
            danisan_listesi_frame, text=danisan, font=("Arial", 14),
            fg_color="#E0E0E0", hover_color="#BDBDBD", text_color=YAZI_RENGI_KOYU,
            command=lambda ad=danisan: danisan_sec_action(ad)
        ).pack(fill="x", padx=10, pady=5)


def hakkinda_sayfasini_goster():
    ekrani_temizle(sadece_icerik=False) 
    header_ve_navbar_ciz() 
    hakkinda_icerigi_ciz(main_container)

def hakkinda_icerigi_ciz(master_frame):
    
    content_box = ctk.CTkScrollableFrame(master_frame, fg_color=BEYAZ_KUTU)
    content_box.pack(pady=20, padx=20, expand=True, fill="both")

    ctk.CTkLabel(content_box, text="Hakkımızda", 
                 font=("Arial", 28), text_color=YAZI_RENGI_KOYU).pack(pady=20, padx=50)

    yazi1 = ("Diyetisyen Danışman Takip sistemine hoş geldiniz. "
             "Bu platform, sağlıklı bir yaşam sürmenize yardımcı olmak, beslenme hedeflerinize "
             "ulaşmanızı kolaylaştırmak ve bu süreçte sizi uzmanlarla bir araya getirmek için tasarlandı.")
    ctk.CTkLabel(content_box, text=yazi1, 
                 font=("Arial", 16), text_color=YAZI_RENGI_KOYU, wraplength=700, justify="left").pack(pady=15, padx=50)
    yazi2 = ("İster kilo almak, ister kilo vermek, ister mevcut formunuzu korumak isteyin; "
             "uygulamamız sayesinde günlük kalori takibinizi yapabilir, öğünlerinizi 'gram' veya 'adet' "
             "bazında kolayca ekleyebilir ve ilerlemenizi adım adım takip edebilirsiniz.")
    ctk.CTkLabel(content_box, text=yazi2, 
                 font=("Arial", 16), text_color=YAZI_RENGI_KOYU, wraplength=700, justify="left").pack(pady=15, padx=50)
    yazi3 = ("Sağlıklı bir gelecek için ilk adımı bugün atın.")
    ctk.CTkLabel(content_box, text=yazi3, 
                 font=("Arial", 16, "bold"), text_color=YAZI_RENGI_KOYU).pack(pady=30, padx=50)


def dummy_ekran_goster(sayfa_adi):
    ekrani_temizle(sadece_icerik=False) 
    header_ve_navbar_ciz() 
    
    content_box = ctk.CTkFrame(main_container, fg_color=BEYAZ_KUTU)
    content_box.pack(pady=20, padx=20, expand=True, fill="both")
    
    ctk.CTkLabel(content_box, text=sayfa_adi, font=("Arial", 32), text_color=YAZI_RENGI_KOYU).pack(pady=100)


def grafik_sayfasini_goster():
    if mevcut_kullanici["id"] is None:
        login_ekranini_ac()
        return

    ekrani_temizle(sadece_icerik=False) 
    header_ve_navbar_ciz() 
    
    ctk.CTkLabel(main_container, text="İlerleme Grafikleriniz", font=("Arial", 28), text_color=YAZI_RENGI_KOYU).pack(pady=20)
    grafik_cercevesi_ciz(main_container, mevcut_kullanici["id"])


def grafik_cercevesi_ciz(master_frame, danisan_id):
    
    kilo_data = get_kilo_gecmisi(danisan_id)
    su_data = get_su_gecmisi(danisan_id)
    
    kilo_df = pd.DataFrame(kilo_data, columns=['Tarih', 'Kilo'])
    su_df = pd.DataFrame(su_data, columns=['Tarih', 'Su (ml)'])
    
    if not kilo_df.empty: kilo_df['Tarih'] = pd.to_datetime(kilo_df['Tarih'])
    if not su_df.empty: su_df['Tarih'] = pd.to_datetime(su_df['Tarih'])

    if kilo_df.empty and su_df.empty:
         kombine_df = pd.DataFrame(columns=['Tarih', 'Kilo', 'Su (ml)'])
    else:
         kombine_df = pd.merge(kilo_df, su_df, on='Tarih', how='outer')
         kombine_df = kombine_df.sort_values('Tarih')
    
    if not kombine_df.empty:
         kombine_df['Tarih_Str'] = kombine_df['Tarih'].dt.strftime('%d %b')
    else:
         kombine_df['Tarih_Str'] = pd.Series(dtype='object')
    
    grafik_ana_frame = ctk.CTkFrame(master_frame, fg_color="transparent")
    grafik_ana_frame.pack(fill='both', expand=True, padx=10, pady=10)

    hedef_kilo_str = mevcut_kullanici.get("hedef_kilo", "70")
    try:
        hedef_kilo_float = float(hedef_kilo_str)
        kilo_min_y = hedef_kilo_float - 10
        kilo_max_y = hedef_kilo_float + 10
    except:
        kilo_min_y = 50
        kilo_max_y = 100
    
    su_max_y = 4000 

    kilo_frame = ctk.CTkFrame(grafik_ana_frame, fg_color=BEYAZ_KUTU)
    kilo_frame.pack(side="left", fill="both", expand=True, padx=5)
    
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    if 'Kilo' in kombine_df.columns and not kombine_df['Kilo'].isnull().all():
        ax1.plot(kombine_df['Tarih_Str'], kombine_df['Kilo'], marker='o', linestyle='-', color='orange')
        ax1.set_title("Kilo Değişim Grafiği")
        ax1.set_ylabel("Kilo (kg)")
        ax1.set_ylim(kilo_min_y, kilo_max_y) 
        
        for i, txt in enumerate(kombine_df['Kilo']):
            if pd.notna(txt): 
                ax1.annotate(f"{txt:.1f}", (kombine_df['Tarih_Str'].iloc[i], txt), textcoords="offset points", xytext=(0,10), ha='center')

        plt.setp(ax1.get_xticklabels(), rotation=30, ha='right')
    else:
        ax1.text(0.5, 0.5, "Kilo verisi yok", horizontalalignment='center', verticalalignment='center', transform=ax1.transAxes, color=YAZI_RENGI_KOYU)
    
    canvas1 = FigureCanvasTkAgg(fig1, master=kilo_frame)
    canvas1.draw()
    canvas1.get_tk_widget().pack(fill='both', expand=True)

    su_frame = ctk.CTkFrame(grafik_ana_frame, fg_color=BEYAZ_KUTU)
    su_frame.pack(side="left", fill="both", expand=True, padx=5)
    
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    if 'Su (ml)' in kombine_df.columns and not kombine_df['Su (ml)'].isnull().all():
        bars = ax2.bar(kombine_df['Tarih_Str'], kombine_df['Su (ml)'], color='blue', width=0.5)
        ax2.set_title("Günlük Su Tüketimi")
        ax2.set_ylabel("Su (ml)")
        ax2.set_ylim(0, su_max_y) 
        
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                 ax2.annotate(f'{int(height)}',
                              xy=(bar.get_x() + bar.get_width() / 2, height),
                              xytext=(0, 3),  
                              textcoords="offset points",
                              ha='center', va='bottom')

        plt.setp(ax2.get_xticklabels(), rotation=30, ha='right')
    else:
        ax2.text(0.5, 0.5, "Su verisi yok", horizontalalignment='center', verticalalignment='center', transform=ax2.transAxes, color=YAZI_RENGI_KOYU)

    canvas2 = FigureCanvasTkAgg(fig2, master=su_frame)
    canvas2.draw()
    canvas2.get_tk_widget().pack(fill='both', expand=True)

    kombine_frame = ctk.CTkFrame(grafik_ana_frame, fg_color=BEYAZ_KUTU)
    kombine_frame.pack(side="left", fill="both", expand=True, padx=5)
    
    fig3, ax3 = plt.subplots(figsize=(5, 4))
    if not kombine_df.empty:
        ax3_su = ax3.twinx() 
        
        if 'Kilo' in kombine_df.columns and not kombine_df['Kilo'].isnull().all():
            ax3.plot(kombine_df['Tarih_Str'], kombine_df['Kilo'], marker='o', linestyle='-', color='orange', label="Kilo (kg)")
            ax3.set_ylabel("Kilo (kg)", color='orange')
            ax3.tick_params(axis='y', labelcolor='orange')
            ax3.set_ylim(kilo_min_y, kilo_max_y) 
        
        if 'Su (ml)' in kombine_df.columns and not kombine_df['Su (ml)'].isnull().all():
            ax3_su.bar(kombine_df['Tarih_Str'], kombine_df['Su (ml)'], color='blue', alpha=0.5, label="Su (ml)", width=0.5)
            ax3_su.set_ylabel("Su (ml)", color='blue')
            ax3_su.tick_params(axis='y', labelcolor='blue')
            ax3_su.set_ylim(0, su_max_y) 

        ax3.set_title("Kombine Kilo ve Su Takibi")
        plt.setp(ax3.get_xticklabels(), rotation=30, ha='right')
    else:
        ax3.text(0.5, 0.5, "Veri yok", horizontalalignment='center', verticalalignment='center', transform=ax3.transAxes, color=YAZI_RENGI_KOYU)

    canvas3 = FigureCanvasTkAgg(fig3, master=kombine_frame)
    canvas3.draw()
    canvas3.get_tk_widget().pack(fill='both', expand=True)


def cikis_yap_action():
    global mevcut_kullanici
    mevcut_kullanici = {
        "id": None, "rol": None,
        "hedef_guncel_kilo": "N/A", "hedef_kilo": "N/A",
        "aktivite_seviyesi": None, "hedef_kalori": "N/A",
        "bugun_su": 0, "son_kilo": "N/A"
    }
    ana_sayfayi_goster() 


def login_ekranini_ac():
    global login_penceresi 
    if login_penceresi is not None and login_penceresi.winfo_exists():
        login_penceresi.focus() 
        return

    login_penceresi = ctk.CTkToplevel(app) 
    login_penceresi.title("Giriş Yap")
    login_penceresi.geometry("400x400")
    login_penceresi.transient(app) 
    
    def login_action_GERCEK():
        girilen_eposta = eposta_entry.get()
        girilen_sifre = sifre_entry.get()
        
        sonuc = kullanici_giris_yap(girilen_eposta, girilen_sifre)

        if sonuc: 
            kullanici_id, rol = sonuc
            
            mevcut_kullanici["id"] = kullanici_id
            mevcut_kullanici["rol"] = rol
            
            login_penceresi.destroy() 
            
            if rol == "Danışan":
                hedef_verisi = hedef_getir(kullanici_id)
                
                if hedef_verisi: 
                    guncel_kilo, hedef_kilo, aktivite, hedef_kalori = hedef_verisi
                    mevcut_kullanici["hedef_guncel_kilo"] = guncel_kilo
                    mevcut_kullanici["hedef_kilo"] = hedef_kilo
                    mevcut_kullanici["aktivite_seviyesi"] = aktivite
                    mevcut_kullanici["hedef_kalori"] = str(int(hedef_kalori or 2000))
                
                ana_sayfayi_goster() 
                
            elif rol == "Diyetisyen":
                ana_sayfayi_goster() 
            
        else: 
            mesaj_labeli.configure(text="E-posta veya Sifre hatali!", text_color="red")
            mevcut_kullanici["id"] = None
            mevcut_kullanici["rol"] = None

    ctk.CTkLabel(login_penceresi, text="Sisteme Giriş Yap", font=("Arial", 24)).pack(pady=30)
    ctk.CTkLabel(login_penceresi, text="E-posta:").pack(padx=30, anchor="w")
    eposta_entry = ctk.CTkEntry(login_penceresi, placeholder_text="eposta@adresiniz.com", width=340)
    eposta_entry.pack(pady=5, padx=30)
    ctk.CTkLabel(login_penceresi, text="Sifre:").pack(padx=30, anchor="w")
    sifre_entry = ctk.CTkEntry(login_penceresi, placeholder_text="Sifreniz", show="*", width=340)
    sifre_entry.pack(pady=5, padx=30)
    mesaj_labeli = ctk.CTkLabel(login_penceresi, text="", font=("Arial", 12))
    mesaj_labeli.pack(pady=20)
    login_button = ctk.CTkButton(login_penceresi, text="Giriş Yap", width=200, height=40, command=login_action_GERCEK)
    login_button.pack(pady=20)


def kayit_ekranini_ac():
    global kayit_penceresi 
    if kayit_penceresi is not None and kayit_penceresi.winfo_exists():
        kayit_penceresi.focus() 
        return
        
    kayit_penceresi = ctk.CTkToplevel(app) 
    kayit_penceresi.title("Yeni Kullanıcı Kaydı")
    kayit_penceresi.geometry("400x800") 
    kayit_penceresi.transient(app) 

    def kayit_action_GERCEK():
        ad = ad_entry.get()
        soyad = soyad_entry.get()
        eposta = eposta_entry.get()
        sifre1 = sifre_entry1.get()
        sifre2 = sifre_entry2.get()
        
        dogum_tarihi = dt_entry.get()
        cinsiyet = cinsiyet_combo.get()
        kan_grubu = kan_combo.get()
        hastaliklar = hastalik_text.get("1.0", "end-1c")
        boy_cm = boy_entry.get() 

        if not ad or not eposta or not sifre1:
            mesaj_labeli.configure(text="Zorunlu alanlari doldurun.", text_color="red")
            return
        if sifre1 != sifre2:
            mesaj_labeli.configure(text="Sifreler uyusmuyor!", text_color="red")
            return
        if dogum_tarihi and len(dogum_tarihi) != 10 and len(dogum_tarihi) != 0: 
             mesaj_labeli.configure(text="Dogum Tarihi formatı GG.AA.YYYY olmalı.", text_color="red")
             return

        kullanici_id = kullanici_kaydet(
            ad=ad, soyad=soyad, eposta=eposta, sifre_duz_metin=sifre1, rol="Danışan",
            dogum_tarihi=dogum_tarihi if dogum_tarihi else None,
            cinsiyet=cinsiyet if cinsiyet != "Seçiniz..." else None,
            kan_grubu=kan_grubu if kan_grubu != "Seçiniz..." else None,
            hastaliklar=hastaliklar,
            boy_cm=boy_cm if boy_cm else None 
        )

        if kullanici_id:
            mesaj_labeli.configure(text="Kayit basarili! Lutfen Giris yapin.", text_color="green")
            app.after(1500, kayit_penceresi.destroy) 
        else:
            mesaj_labeli.configure(text="Hata: E-posta zaten kayitli olabilir.", text_color="red")

    ctk.CTkLabel(kayit_penceresi, text="Yeni Kullanıcı Kaydı", font=("Arial", 24)).pack(pady=20)
    
    form_frame = ctk.CTkScrollableFrame(kayit_penceresi, width=360, height=500)
    form_frame.pack(fill="x")
    
    ctk.CTkLabel(form_frame, text="Ad:").pack(padx=30, anchor="w")
    ad_entry = ctk.CTkEntry(form_frame, placeholder_text="Adiniz", width=340)
    ad_entry.pack(pady=(0,10), padx=30)
    
    ctk.CTkLabel(form_frame, text="Soyad:").pack(padx=30, anchor="w")
    soyad_entry = ctk.CTkEntry(form_frame, placeholder_text="Soyadiniz", width=340)
    soyad_entry.pack(pady=(0,10), padx=30)
    
    ctk.CTkLabel(form_frame, text="E-posta:").pack(padx=30, anchor="w")
    eposta_entry = ctk.CTkEntry(form_frame, placeholder_text="eposta@adresiniz.com", width=340)
    eposta_entry.pack(pady=(0,10), padx=30)
    
    ctk.CTkLabel(form_frame, text="Sifre:").pack(padx=30, anchor="w")
    sifre_entry1 = ctk.CTkEntry(form_frame, placeholder_text="Guclu bir sifre secin", show="*", width=340)
    sifre_entry1.pack(pady=(0,10), padx=30)
    
    ctk.CTkLabel(form_frame, text="Sifre (Tekrar):").pack(padx=30, anchor="w")
    sifre_entry2 = ctk.CTkEntry(form_frame, placeholder_text="Sifrenizi tekrar girin", show="*", width=340)
    sifre_entry2.pack(pady=(0,10), padx=30)
    
    ctk.CTkLabel(form_frame, text="Doğum Tarihi:").pack(padx=30, anchor="w")
    dt_entry = ctk.CTkEntry(form_frame, placeholder_text="GG.AA.YYYY (Zorunlu degil)", width=340)
    dt_entry.pack(pady=(0,10), padx=30)

    ctk.CTkLabel(form_frame, text="Boy (cm):").pack(padx=30, anchor="w")
    boy_entry = ctk.CTkEntry(form_frame, placeholder_text="Orn: 175 (Zorunlu degil)", width=340)
    boy_entry.pack(pady=(0,10), padx=30)
    
    ctk.CTkLabel(form_frame, text="Cinsiyet:").pack(padx=30, anchor="w")
    cinsiyet_combo = ctk.CTkComboBox(form_frame, values=["Seçiniz...", "Erkek", "Kadın", "Belirtmek istemiyorum"], width=340)
    cinsiyet_combo.pack(pady=(0,10), padx=30)
    
    ctk.CTkLabel(form_frame, text="Kan Grubu:").pack(padx=30, anchor="w")
    kan_combo = ctk.CTkComboBox(form_frame, values=["Seçiniz...", "A+", "A-", "B+", "B-", "AB+", "AB-", "0+", "0-", "Bilmiyorum"], width=340)
    kan_combo.pack(pady=(0,10), padx=30)
    
    ctk.CTkLabel(form_frame, text="Bilinen Hastalıklar (varsa):").pack(padx=30, anchor="w")
    hastalik_text = ctk.CTkTextbox(form_frame, width=340, height=100)
    hastalik_text.pack(pady=(0,10), padx=30)

    mesaj_labeli = ctk.CTkLabel(kayit_penceresi, text="", font=("Arial", 12))
    mesaj_labeli.pack(pady=10)
    kayit_butonu = ctk.CTkButton(kayit_penceresi, text="Kaydı Tamamla", width=200, height=40, command=kayit_action_GERCEK)
    kayit_butonu.pack(pady=10)


if __name__ == "__main__":
    
    try:
        locale.setlocale(locale.LC_TIME, "Turkish") 
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, "tr_TR.UTF-8")
        except locale.Error:
            pass
    
    tablo_olustur() 
    varsayilan_yemekleri_yukle() 
    
    ana_sayfayi_goster() 
    app.mainloop()