#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.topo import Topo

class ProjeTopo(Topo):
    "Bitirme projesi için basitleştirilmiş kurumsal ağ topolojisi"

    def build(self):
        
        # 1. Switchleri Ekle (Omurga, Merkez, Şube)
        # s1: Veri Merkezi'ndeki ana Omurga SDN Switch
        s1 = self.addSwitch('s1', cls=OVSSwitch, protocols='OpenFlow13', dpid='0000000000000001')
        
        # s_merkez: Merkez lokasyonundaki L2 Switch
        s_merkez = self.addSwitch('s_merkez', cls=OVSSwitch, protocols='OpenFlow13', dpid='0000000000000002')
        
        # s_sube: Şube lokasyonundaki L2 Switch
        s_sube = self.addSwitch('s_sube', cls=OVSSwitch, protocols='OpenFlow13' , dpid='0000000000000003')

        # 2. Hostları Ekle (GERÇEK TOPOLOJİ - FARKLI SUBNETLER)
        
        # Veri Merkezi Ağı (10.0.1.0/24) - Gateway: 10.0.1.1
        srv1 = self.addHost('srv1', ip='10.0.1.10/24', defaultRoute='via 10.0.1.1', mac='00:00:00:00:01:10')
        srv2 = self.addHost('srv2', ip='10.0.1.11/24', defaultRoute='via 10.0.1.1', mac='00:00:00:00:01:11')

        # Merkez Ofis Ağı (10.0.2.0/24) - Gateway: 10.0.2.1
        h_merkez = self.addHost('h_merkez', ip='10.0.2.20/24', defaultRoute='via 10.0.2.1', mac='00:00:00:00:02:20')

        # Şube Ağı (10.0.3.0/24) - Gateway: 10.0.3.1
        h_sube = self.addHost('h_sube', ip='10.0.3.30/24', defaultRoute='via 10.0.3.1', mac='00:00:00:00:03:30')
        # 3. Linkleri Ekle
        
        # Veri Merkezi Sunucularını Omurga Switch'e bağla
        self.addLink(srv1, s1)
        self.addLink(srv2, s1)

        # Merkez PC'sini Merkez Switch'e bağla
        self.addLink(h_merkez, s_merkez)

        # Şube PC'sini Şube Switch'ine bağla
        self.addLink(h_sube, s_sube)
        
        # Ana switch'leri birbirine bağla (WAN linklerini temsil ediyor)
        self.addLink(s1, s_merkez)
        self.addLink(s1, s_sube)


# Mininet'in bu topolojiyi tanıması için
topos = { 'projettopo': ( lambda: ProjeTopo() ) }

# Bu script doğrudan çalıştırılırsa Mininet'i başlatan kod
if __name__ == '__main__':
    setLogLevel('info')
    
    # Kontrolcü olarak Ryu'yu (localde 6653 portunda) gösteriyoruz
    c0 = RemoteController('c0', ip='127.0.0.1', port=6653)
    
    topo = ProjeTopo()
    net = Mininet(topo=topo, controller=c0, build=False, autoSetMacs=True)
    
    net.build()
    net.start()
    
    print("*** Topoloji başarıyla başlatıldı.")
    print("*** CLI'a geçiliyor. Çıkmak için 'exit' yazın.")
    CLI(net)
    
    print("*** Ağ durduruluyor.")
    net.stop()
