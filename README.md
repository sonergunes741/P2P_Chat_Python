# 💬 P2P Chat - Serverless LAN Messenger

**Modern, güvenli ve kullanımı kolay Peer-to-Peer sohbet uygulaması**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()

---

## ✨ Özellikler

- 🚀 **Anında Başlat** - Kurulum gerektirmez, çalıştır ve konuş
- 🔍 **Otomatik Keşif** - Ağdaki diğer kullanıcıları tek tıkla bul
- 🛡️ **Güvenli** - Onaylamadığınız kişiler size mesaj atamaz
- 🎨 **Modern Arayüz** - Dark theme, kullanımı kolay GUI
- 📱 **Kullanıcı Dostu** - Username, IP ve port bilgileri açıkça görünür
- 🔌 **Sunucusuz** - Merkezi sunucu yok, direkt P2P bağlantı
- 🌐 **Cross-Platform** - Windows, Linux ve macOS

---

## 🚀 Hızlı Başlangıç

### 1️⃣ Gereksinimler
- Python 3.8+ (Sadece standart kütüphane)

### 2️⃣ Kurulum
```bash
git clone https://github.com/sonergunes741/P2P_Chat_Python.git
cd P2P_Chat_Python
```

### 3️⃣ Çalıştır
```bash
python gui_main.py
```

İlk açılışta:
1. **Kullanıcı Adı** gir
2. **Port** seç (varsayılan: 5000)
3. **START SESSION** butonuna bas

> 🔒 **Firewall Uyarısı:** İlk açılışta Windows/macOS firewall izin isteyecektir - **Allow/İzin Ver** seçeneğini seçin.

---

## 📖 Nasıl Kullanılır?

### Birini Bul ve Bağlan
1. **SCAN NETWORK** butonuna bas
2. Found Peers listesinden birini seç
3. **CONNECT** butonuna bas
4. Karşı tarafta ACCEPT/REJECT butonları görünür
5. **ACCEPT** denirse bağlantı kurulur

### Mesaj At
- Bağlı olduğun kişiler "Connected Peers" listesinde ✓ işaretiyle görünür
- Alt kısımdaki mesaj kutusuna yaz ve **SEND** bas veya **Enter**'a bas

### Bağlantıyı Kes
- Connected Peers'dan birini seç
- **DISCONNECT** butonuna bas

---

## 🔧 Aynı Bilgisayarda Test

Farklı portlar kullanarak aynı PC'de birden fazla kullanıcı oluştur:

**Terminal 1:**
```bash
python gui_main.py
# Port: 5000, Username: Ali
```

**Terminal 2:**
```bash
python gui_main.py
# Port: 5001, Username: Veli
```

Scan yap → Birbirinizi bulun → Bağlanın!

---

## 🏗️ Proje Yapısı

```
P2P_Chat_Python/
├── src/
│   ├── gui.py              # Ana GUI (Tkinter)
│   ├── peer.py             # Peer yönetimi
│   ├── discovery.py        # UDP broadcast keşif
│   ├── connection.py       # TCP bağlantı yöneticisi
│   ├── protocol.py         # Mesaj protokolü
│   └── startup_dialog.py   # Başlangıç ekranı
├── gui_main.py             # GUI başlatıcı
├── main.py                 # CLI başlatıcı
└── README.md
```

---

## ❓ Sık Sorulan Sorular

**Q: Diğer kullanıcıları göremiyorum?**
- Aynı Wi-Fi/LAN ağında olduğunuzdan emin olun
- Firewall izinlerini kontrol edin (TCP 5000, UDP 5001)

**Q: Bağlantı kuruluyor ama mesaj alamıyorum?**
- Karşı tarafın bağlantıyı ACCEPT ettiğinden emin olun
- Connected Peers listesinde ✓ işareti görünmeli

**Q: Farklı port nasıl kullanırım?**
- Startup Dialog'da port dropdown'ından seçin
- CLI: `python gui_main.py --port 5002`

---

## 🛠️ Gelişmiş Kullanım

### CLI Modu
```bash
python main.py --port 5000
```

Komutlar:
- `discover` - Ağı tara
- `connect <IP>` - Bağlan
- `send <mesaj>` - Mesaj gönder
- `exit` - Çıkış

### Build .exe (Windows)
```bash
pip install pyinstaller
python build.py
```
`dist/P2P_Chat.exe` oluşacak

---

## 🧪 Teknik Detaylar

- **Discovery:** UDP Broadcast (Port 5001)
- **Communication:** TCP (Port 5000+ seçilebilir)
- **Protocol:** JSON-based message format
- **Handshake:** Connection Request/Accept/Reject
- **Threading:** Async message handling

---

## 👥 Ekip

- **Soner Güneş** (240104004201)
- **Ömer Faruk Olkay** (210104004039)
- **Ahmet Baha Çepni** (2101040040xx)

---

## 📜 Lisans

MIT License - Educational Purpose Project

**Ağ Programlama Dersi | Network Programming Course**
