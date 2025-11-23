🛡️ SDN Tabanlı Dinamik Router ve Akıllı Güvenlik Duvarı

Bu proje, Yazılım Tanımlı Ağlar (SDN) mimarisi kullanılarak geliştirilmiş; Dinamik Yönlendirme (Dijkstra Algoritması), ağ topolojisi keşfi ve güvenlik duvarı özelliklerine sahip ileri seviye bir ağ kontrolcüsüdür.

📋 Proje Hakkında

Geleneksel ağ cihazlarının statik yapısını ortadan kaldırarak, ağ yönetimini merkezi bir Python kodu üzerinden (Ryu Controller) dinamik olarak gerçekleştirmeyi amaçlar.

Temel Özellikler:

🧠 Dinamik Yönlendirme: Ağ haritasını (Topology) otomatik keşfeder ve Dijkstra Algoritması ile en kısa yolu hesaplar.

🌐 L3 Routing: Farklı IP subnetleri arasında otomatik paket yönlendirme yapar.

🛡️ Firewall: Şube -> Veri Merkezi gibi belirlenen kurallara göre yasaklı trafiği L3 seviyesinde engeller.

⚡ Sanal Gateway: ARP isteklerini otomatik yanıtlayan akıllı sanal ağ geçidi.

🛠️ Kurulum

Bu projeyi çalıştırmak için Ubuntu/Linux üzerinde aşağıdaki araçların kurulu olması gerekir:

Mininet: Ağ simülasyonu için.

Ryu Controller: SDN kontrolcüsü olarak.

Python 3 & NetworkX: Kodların ve algoritmaların çalışması için.

Gerekli Kütüphaneler:

sudo pip3 install eventlet==0.30.2 networkx


🚀 Nasıl Çalıştırılır? (Dinamik Mod)

Projeyi çalıştırmak için iki ayrı terminal kullanın.

Adım 1: Kontrolcüyü Başlatın (Terminal 1)
SDN beynini "Topology Discovery" modunda başlatın:

ryu-manager dinamic_router.py --observe-links


(Terminalde "Switch bağlandı" yazılarını görene kadar bekleyin)

Adım 2: Ağı Başlatın (Terminal 2)
Mininet topolojisini oluşturun:

sudo python3 proje_topolojim.py


⚠️ Önemli: Mininet açıldıktan sonra 5-10 saniye bekleyin. Kontrolcünün ağ haritasını (LLDP ile) çıkarması zaman alır.

🧪 Test Senaryoları

Sistem çalıştıktan sonra Mininet konsolunda (mininet>) şu testleri yapabilirsiniz:

1. Dinamik Rota Testi (Başarılı Olmalı)
Merkez ofis bilgisayarının sunucuya erişimi:

mininet> h_merkez ping -c 3 srv1


Beklenen Sonuç: %0 Packet Loss (Kontrolcü en kısa yolu hesaplayıp iletir)

2. Güvenlik Testi (Engellenmeli)
Şube ofisinin sunucuya erişimi (Yasaklı Trafik):

mininet> h_sube ping -c 3 srv1


Beklenen Sonuç: %100 Packet Loss (Firewall engelledi)

🗺️ Ağ Yapısı (Topoloji)

Proje, aşağıdaki mimari üzerinde koşmaktadır. Fiziksel bağlantılar sabit olsa da, trafik akışı kontrolcü tarafından dinamik olarak belirlenir.

graph TD
    %% Stiller
    classDef switch fill:#f9f,stroke:#333,stroke-width:2px;
    classDef pc fill:#ccf,stroke:#333,stroke-width:2px;
    classDef sdn fill:#ff9,stroke:#333,stroke-width:4px;
    classDef server fill:#cfc,stroke:#333,stroke-width:2px;

    %% SDN Kontrolcü
    Controller[🧠 Ryu SDN Kontrolcüsü<br/>(Dinamik Router + Firewall)]:::sdn

    %% Veri Merkezi
    subgraph DC [🏢 Veri Merkezi (10.0.1.0/24)]
        direction TB
        S1[S1: Omurga Switch]:::switch
        Srv1[🖥️ Srv1: App Server]:::server
        Srv2[🗄️ Srv2: DB Server]:::server
        S1 --- Srv1
        S1 --- Srv2
    end

    %% Merkez Ofis
    subgraph HQ [🏢 Merkez Ofis (10.0.2.0/24)]
        direction TB
        S2[S2: Merkez Switch]:::switch
        PC_Merkez[💻 H_Merkez]:::pc
        PC_Merkez --- S2
    end

    %% Şube Ofis
    subgraph Branch [🏠 Şube Ofis (10.0.3.0/24)]
        direction TB
        S3[S3: Şube Switch]:::switch
        PC_Sube[💻 H_Sube]:::pc
        PC_Sube --- S3
    end

    %% Bağlantılar
    S2 ==(WAN Link)==> S1
    S3 ==(WAN Link)==> S1

    %% Kontrolcü Bağlantıları
    Controller -.->|LLDP & OpenFlow| S1
    Controller -.->|LLDP & OpenFlow| S2
    Controller -.->|LLDP & OpenFlow| S3


👨‍💻 Geliştirici Notları

v1.0 (Eski): Statik yönlendirme kullanıyordu.

v2.0 (Güncel): NetworkX kütüphanesi entegre edildi. Ağ topolojisi dinamik olarak keşfediliyor ve paketler Dijkstra En Kısa Yol Algoritması ile hedefe ulaştırılıyor.