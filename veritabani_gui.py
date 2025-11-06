import psycopg2
import tkinter as tk
from tkinter import messagebox, ttk

# PostgreSQL bağlantısı
def baglanti_olustur():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="ruhicenet123",
            port="5432"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Bağlantı Hatası", str(e))
        return None


# Kullanıcı ekleme
def kullanici_ekle():
    ad = entry_ad.get()
    soyad = entry_soyad.get()
    email = entry_email.get()

    if not ad or not soyad or not email:
        messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldur.")
        return

    conn = baglanti_olustur()
    if conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO kullanicilar (ad, soyad, email) VALUES (%s, %s, %s)", (ad, soyad, email))
        conn.commit()
        conn.close()
        messagebox.showinfo("Başarılı", "Kullanıcı eklendi.")
        listeyi_guncelle()


# Kullanıcıları listeleme
def listeyi_guncelle():
    for item in tree.get_children():
        tree.delete(item)

    conn = baglanti_olustur()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM kullanicilar ORDER BY id ASC")
        rows = cur.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        conn.close()


# Kullanıcı silme
def kullanici_sil():
    secilen = tree.selection()
    if not secilen:
        messagebox.showwarning("Uyarı", "Silmek için bir kullanıcı seçin.")
        return

    id = tree.item(secilen[0])["values"][0]
    conn = baglanti_olustur()
    if conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM kullanicilar WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Silindi", "Kullanıcı silindi.")
        listeyi_guncelle()


# Ana pencere
pencere = tk.Tk()
pencere.title("Veritabanı Yönetimi")
pencere.geometry("600x400")
pencere.configure(bg="#2b2b2b")

# Başlık
label_baslik = tk.Label(pencere, text="KULLANICI YÖNETİMİ", bg="#2b2b2b", fg="#c86464", font=("Arial", 16, "bold"))
label_baslik.pack(pady=10)

# Girdi alanları
frame_girdi = tk.Frame(pencere, bg="#2b2b2b")
frame_girdi.pack(pady=10)

tk.Label(frame_girdi, text="Ad:", bg="#2b2b2b", fg="white").grid(row=0, column=0)
entry_ad = tk.Entry(frame_girdi)
entry_ad.grid(row=0, column=1, padx=5)

tk.Label(frame_girdi, text="Soyad:", bg="#2b2b2b", fg="white").grid(row=1, column=0)
entry_soyad = tk.Entry(frame_girdi)
entry_soyad.grid(row=1, column=1, padx=5)

tk.Label(frame_girdi, text="E-posta:", bg="#2b2b2b", fg="white").grid(row=2, column=0)
entry_email = tk.Entry(frame_girdi)
entry_email.grid(row=2, column=1, padx=5)

# Butonlar
frame_buton = tk.Frame(pencere, bg="#2b2b2b")
frame_buton.pack(pady=10)

tk.Button(frame_buton, text="Ekle", command=kullanici_ekle, bg="#c86464", fg="white", width=10).grid(row=0, column=0, padx=5)
tk.Button(frame_buton, text="Listele", command=listeyi_guncelle, bg="#c86464", fg="white", width=10).grid(row=0, column=1, padx=5)
tk.Button(frame_buton, text="Sil", command=kullanici_sil, bg="#c86464", fg="white", width=10).grid(row=0, column=2, padx=5)

# Tablo
frame_tablo = tk.Frame(pencere)
frame_tablo.pack(pady=10)

tree = ttk.Treeview(frame_tablo, columns=("ID", "Ad", "Soyad", "Email"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Ad", text="Ad")
tree.heading("Soyad", text="Soyad")
tree.heading("Email", text="E-posta")
tree.pack()

listeyi_guncelle()

pencere.mainloop()
