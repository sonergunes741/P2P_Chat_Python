# ⚡ P2P Chat Application

**Serverless, Secure, and Cross-Platform Peer-to-Peer Communication Tool**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()

Please scroll down for **Turkish (Türkçe)** explanation.

---

## 🇺🇸 English Overview

P2P Chat is a robust messaging application that allows users to communicate directly over a Local Area Network (LAN) without needing a central server. It features a modern Engineer-style GUI, automatic peer discovery, and secure connection handshakes.

### Key Features
*   **📡 Serverless:** True Peer-to-Peer architecture.
*   **🔍 Auto-Discovery:** Find other users on the network automatically via UDP broadcast.
*   **🛡️ Secure Handshake:** Users must approve connection requests before chatting.
*   **💻 Cross-Platform:** Runs on Windows, Linux, and macOS.
*   **🎛️ Dual Interface:** Comes with both a Professional GUI and a Command-Line Interface (CLI).
*   **📦 Easy Setup:** Includes a standalone Windows Installer.

---

## 🇹🇷 Türkçe Proje Tanıtımı

Bu proje, merkezi bir sunucuya ihtiyaç duymadan, yerel ağ (LAN) üzerindeki bilgisayarların doğrudan birbiriyle haberleşmesini sağlayan gelişmiş bir sohbet uygulamasıdır. Ağ programlama ve dağıtık sistemler dersi kapsamında geliştirilmiştir.

### 🌟 Temel Özellikler
1.  **Sunucusuz İletişim:** Mesajlar internete çıkmadan, doğrudan cihazlar arasında gider.
2.  **Otomatik Keşif:** "Ağı Tara" butonu ile aynı ağdaki diğer kullanıcıları otomatik bulur.
3.  **Güvenli Bağlantı:** Biri size bağlanmak istediğinde **Onay/Red** ekranı çıkar. Tanımadığınız kişi size mesaj atamaz.
4.  **Mühendis Arayüzü:** Koyu modlu, sade ve işlevsel Grafik Arayüz (GUI).
5.  **Platform Bağımsız:** Windows, Linux ve macOS üzerinde çalışır.

---

## 📥 Kurulum ve Çalıştırma (Installation)

Uygulamayı çalıştırmanın iki yolu vardır:
1.  **Son Kullanıcı (Kolay Yol):** Hazır kurulum dosyasını kullanmak.
2.  **Geliştirici (Kod Yolu):** Python kodlarını çalıştırmak.

### Yöntem 1: Windows Installer ile Kurulum (Önerilen) ✨
Kodlarla uğraşmak istemiyorsanız:
1.  `installer/` klasöründeki `P2P_Chat_Setup.exe` dosyasını indirin ve kurun.
2.  Masaüstündeki **P2P Chat** ikonuna çift tıklayın.
3.  **Önemli:** İlk açılışta Windows Güvenlik Duvarı sorarsa **"Erişime İzin Ver" (Allow Access)** diyerek onaylayın.

### Yöntem 2: Python ile Çalıştırma
Geliştiriciler veya kaynak koddan çalıştırmak isteyenler için:

**Gereksinimler:**
*   Python 3.8 veya üzeri yüklü olmalıdır.

**Adımlar:**
1.  Projeyi indirin:
    ```bash
    git clone https://github.com/sonergunes741/P2P_Chat_Python.git
    cd P2P_Chat_Python
    ```
2.  Gerekli kütüphaneleri yükleyin (Sadece standart kütüphane kullanılır, ekstra pip install gerekmez ama yine de `requirements.txt` kontrol edilebilir):
    ```bash
    pip install -r requirements.txt
    ```
3.  Uygulamayı başlatın:
    ```bash
    # Grafik Arayüz (GUI) için:
    python gui_main.py

    # Komut Satırı (CLI) için:
    python main.py
    ```

**🔥 Aynı Bilgisayarda Test Etmek İçin:**
İki farklı terminal açın ve farklı portlar kullanın:
*   Terminal 1: `python gui_main.py`
*   Terminal 2: `python gui_main.py --port 5002`

---

## 🛠️ Exe Oluşturma (Build)

Kendi `.exe` dosyanızı veya kurulum paketinizi oluşturmak isterseniz:

1.  **PyInstaller Yükleyin:**
    ```bash
    pip install pyinstaller
    ```
2.  **Build Scriptini Çalıştırın:**
    ```bash
    python build.py
    ```
    Bu işlem `dist/` klasöründe `P2P_Chat.exe` oluşturacaktır.

3.  **Installer Oluşturma (Opsiyonel):**
    *   [Inno Setup](https://jrsoftware.org/isinfo.php) programını indirin.
    *   `installer.iss` dosyasını Inno Setup ile açıp "Compile" butonuna basın.

---

## ⚠️ Sorun Giderme (Troubleshooting)

**S: Diğer bilgisayarı göremiyorum?**
*   **C:** İki bilgisayarın da aynı Wi-Fi/Ağ üzerinde olduğundan emin olun.
*   **C:** **Windows Güvenlik Duvarı (Firewall)** engelini kontrol edin. TCP 5000 ve UDP 5001 portlarına izin verilmelidir. Installer sürümü bunu otomatik yapar.

**S: Bağlanıyorum ama mesaj gitmiyor?**
*   **C:** Bağlantı kurulduğunda sağ üstte "Onay Bekliyor" uyarısı çıkar. **ACCEPT** butonuna basarak bağlantıyı onaylamanız gerekir.

---

## 👥 Ekip Üyeleri (Team)

*   **240104004201** Soner Güneş
*   **210104004039** Ömer Faruk Olkay
*   **2101040040xx** Ahmet Baha Çepni

---
*Educational Purpose Project - Network Programming*
