import netifaces
from pysnmp.entity.rfc3413.oneliner import cmdgen
import time

def remove_duplicates(l):
    return list( dict.fromkeys(l))

def ip_cidr_route_next_hop(snmp_agent_host, snmp_port, snmp_community):
    cmdGen = cmdgen.CommandGenerator()

    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.bulkCmd(
        cmdgen.CommunityData(snmp_community),
        cmdgen.UdpTransportTarget((snmp_agent_host, snmp_port)),
        0, 25,
        '1.3.6.1.2.1.4.24.4.1.4'
    )

    if errorIndication:
        return None
    else:
        if errorStatus:
            return None
        else:
            for binds in varBinds:
                for bind, ip_bin in binds:
                    ip_dec = '.'.join(map(str, ip_bin))
                    if ip_dec != '0.0.0.0':
                        yield ip_dec
    return None


def walk_and_print(default_snmp_agent_host_list, snmp_port, snmp_community):
    for snmp_agent_host in default_snmp_agent_host_list:
        new_snmp_agent_host = ip_cidr_route_next_hop(snmp_agent_host, snmp_port, snmp_community)
        if not new_snmp_agent_host:
            return
        new_snmp_agent_host = list(new_snmp_agent_host)
        if len(new_snmp_agent_host) == 0:
            return
        print("Hopping from " + str(snmp_agent_host) + " to "+ str(remove_duplicates(new_snmp_agent_host)))
        walk_and_print(new_snmp_agent_host, snmp_port, snmp_community)

if __name__ == '__main__':
    print("Starting program")
    gateways = netifaces.gateways()
    gateways_ips = [info[0] for info in gateways.pop("default").values()]
    gateways_ips = gateways_ips + [info[0] for garray in gateways.values() for info in garray]
    gateways_ips = remove_duplicates(gateways_ips)
    print("Gateway IPs: " + str(gateways_ips))



    snmp_agent_host_list = gateways_ips
    SNMP_PORT = 161
    SNMP_COMMUNITY = 'PSIPUB'
    walk_and_print(snmp_agent_host_list, SNMP_PORT, SNMP_COMMUNITY)

