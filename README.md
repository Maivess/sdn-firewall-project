# 🛡️ SDN Tabanlı Akıllı Güvenlik Duvarı ve L3 Yönlendirici

Bu proje, Yazılım Tanımlı Ağlar (SDN) mimarisi kullanılarak geliştirilmiş; paket analizi, statik yönlendirme ve güvenlik duvarı özelliklerine sahip bir ağ kontrolcüsüdür.

---

## 📋 Proje Hakkında

Geleneksel ağ cihazlarının hantal yapısını ortadan kaldırarak, ağ yönetimini merkezi bir **Python** kodu üzerinden (Ryu Controller) gerçekleştirmeyi amaçlar.

**Temel Özellikler:**
* **L3 Routing:** Farklı IP blokları (10.0.1.0/24, 10.0.2.0/24 vb.) arasında paket yönlendirme.
* **Firewall:** Belirlenen kurallara göre (örn: Şube -> Veri Merkezi) trafiği engelleme.
* **Sanal Gateway:** ARP isteklerini otomatik yanıtlayan sanal ağ geçidi.

---

## 🛠️ Kurulum

Bu projeyi çalıştırmak için **Ubuntu/Linux** üzerinde aşağıdaki araçların kurulu olması gerekir:

1.  **Mininet:** Ağ simülasyonu için.
2.  **Ryu Controller:** SDN kontrolcüsü olarak.
3.  **Python 3:** Kodların çalışması için.

**Gerekli Kütüphaneler:**
```bash
sudo pip3 install eventlet==0.30.2 networkx


Nasıl Çalıştırılır?
Projeyi çalıştırmak için iki ayrı terminal kullanmanız önerilir.

Adım 1: Kontrolcüyü Başlatın (Terminal 1) Önce SDN beynini ayağa kaldırın:

Bash

ryu-manager firewall.py
(Terminalde "Switch bağlandı" yazılarını görene kadar bekleyin)

Adım 2: Ağı Başlatın (Terminal 2) Mininet topolojisini oluşturun:

Bash

sudo python3 proje_topolojim.py
🧪 Test Senaryoları
Sistem çalıştıktan sonra Mininet konsolunda (mininet>) şu testleri yapabilirsiniz:

1. Erişim Testi (Başarılı Olmalı) Merkez ofis bilgisayarının sunucuya erişimi:

Bash

mininet> h_merkez ping -c 3 srv1
Beklenen Sonuç: %0 Packet Loss (İletişim var)

2. Güvenlik Testi (Engellenmeli) Şube ofisinin sunucuya erişimi (Yasaklı Trafik):

Bash

mininet> h_sube ping -c 3 srv1
Beklenen Sonuç: %100 Packet Loss (Firewall engelledi)

🗺️ Ağ Yapısı (Topoloji)
S1 (Omurga): Veri Merkezi (Serverlar buraya bağlı)

S2 (Merkez): Merkez Ofis PC'leri (10.0.2.x)

S3 (Şube): Şube Ofis PC'leri (10.0.3.x) - Kısıtlı Erişim

👨‍💻 Geliştirici Notları
Şu anki sürüm (v1.0) Statik Yönlendirme kullanmaktadır.

Döngüleri (loop) engellemek için port yönlendirmeleri manuel tanımlanmıştır.

Gelecek sürümlerde Dinamik Yönlendirme (Dijkstra) eklenecektir.