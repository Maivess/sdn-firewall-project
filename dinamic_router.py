# Gerekli Kütüphaneler
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet, arp, ipv4, icmp
from ryu.lib.packet import ether_types
# TOPOLOJİ İÇİN GEREKLİ KÜTÜPHANELER DÜZELTİLDİ
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link
import networkx as nx

class DynamicL3Router(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(DynamicL3Router, self).__init__(*args, **kwargs)
        
        self.router_mac = '00:00:00:00:00:99'
        self.net = nx.DiGraph()
        
        self.arp_table = {
            '10.0.1.10': '00:00:00:00:01:10', 
            '10.0.1.11': '00:00:00:00:01:11', 
            '10.0.2.20': '00:00:00:00:02:20', 
            '10.0.3.30': '00:00:00:00:03:30'  
        }

        self.host_location = {
            '10.0.1.10': 1,
            '10.0.1.11': 1,
            '10.0.2.20': 2,
            '10.0.3.30': 3
        }

    # --- TOPOLOJİ KEŞFİ DÜZELTİLDİ ---
    # EventTopologyChange yerine EventSwitchEnter kullanıyoruz.
    # Bu olay, bir switch ağa katıldığında veya durum değiştiğinde tetiklenir.
    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        # Linkleri al
        links_list = get_link(self, None)
        
        # Switchleri al
        switch_list = get_switch(self, None)
        
        # Grafiği temizle (Sıfırdan kurmak en temizidir)
        self.net.clear()
        
        # Düğümleri ekle
        switches_nodes = [switch.dp.id for switch in switch_list]
        self.net.add_nodes_from(switches_nodes)
        
        # Kenarları (Linkleri) ekle
        links = [(link.src.dpid, link.dst.dpid, {'port': link.src.port_no}) for link in links_list]
        self.net.add_edges_from(links)
        
        # Ters yönleri de ekle
        links_reverse = [(link.dst.dpid, link.src.dpid, {'port': link.dst.port_no}) for link in links_list]
        self.net.add_edges_from(links_reverse)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        self.logger.info("Switch %s bağlandı.", datapath.id)
        
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id if buffer_id else ofproto.OFP_NO_BUFFER,
                                priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP: return

        arp_pkt = pkt.get_protocol(arp.arp)
        if arp_pkt:
            self.handle_arp(datapath, in_port, eth, arp_pkt)
            return

        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        if ip_pkt:
            src_ip = ip_pkt.src
            dst_ip = ip_pkt.dst

            if src_ip == '10.0.3.30' and dst_ip == '10.0.1.10':
                 self.logger.warning("!!! DİNAMİK FIREWALL: %s -> %s BLOKLANDI !!!", src_ip, dst_ip)
                 return 

            if dst_ip in self.arp_table:
                dst_mac = self.arp_table[dst_ip]
                if dst_ip in self.host_location:
                    dst_dpid = self.host_location[dst_ip]
                    self.route_packet(msg, dpid, dst_ip, dst_mac, dst_dpid)

    def handle_arp(self, datapath, in_port, eth, arp_pkt):
        if arp_pkt.opcode == arp.ARP_REQUEST:
            if arp_pkt.dst_ip in ['10.0.1.1', '10.0.2.1', '10.0.3.1']:
                pkt = packet.Packet()
                pkt.add_protocol(ethernet.ethernet(ethertype=ether_types.ETH_TYPE_ARP,
                                                   dst=eth.src, src=self.router_mac))
                pkt.add_protocol(arp.arp(opcode=arp.ARP_REPLY,
                                         src_mac=self.router_mac, src_ip=arp_pkt.dst_ip,
                                         dst_mac=arp_pkt.src_mac, dst_ip=arp_pkt.src_ip))
                self._send_packet(datapath, in_port, pkt)

    def route_packet(self, msg, current_dpid, dst_ip, dst_mac, dst_switch_dpid):
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        out_port = None

        if current_dpid == dst_switch_dpid:
            if dst_ip == '10.0.1.10': out_port = 1
            elif dst_ip == '10.0.1.11': out_port = 2
            elif dst_ip == '10.0.2.20': out_port = 1
            elif dst_ip == '10.0.3.30': out_port = 1
        else:
            try:
                # Topoloji verisi henüz oluşmadıysa tekrar dene
                if not self.net.has_node(current_dpid) or not self.net.has_node(dst_switch_dpid):
                    # Linkleri manuel tetikle
                    self.get_topology_data(None)
                    
                path = nx.shortest_path(self.net, current_dpid, dst_switch_dpid)
                next_hop = path[1]
                out_port = self.net[current_dpid][next_hop]['port']
            except Exception as e:
                # self.logger.info("Yol bulunamadı: %s", e)
                return

        if out_port:
            actions = [parser.OFPActionOutput(out_port)]
            new_eth = ethernet.ethernet(ethertype=ether_types.ETH_TYPE_IP,
                                        dst=dst_mac, src=self.router_mac)
            pkt_out = packet.Packet()
            pkt_out.add_protocol(new_eth)
            pkt_out.add_protocol(msg.data[14:]) 
            self._send_packet(datapath, out_port, pkt_out)

    def _send_packet(self, datapath, port, pkt):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt.serialize()
        data = pkt.data
        actions = [parser.OFPActionOutput(port)]
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=data)
        datapath.send_msg(out)