#!/bin/bash

# Actualitza els paquets i instal·la WireGuard
sudo apt update
sudo apt install wireguard -y

# Genera claus per al client
wg genkey | tee privatekey_client | wg pubkey > publickey_client

# Per veure les claus
cat privatekey_client
cat publickey_client

# Crea l'arxiu de configuració de WireGuard
sudo nano /etc/wireguard/wg0.conf
[Interface]
PrivateKey = <clau_privada_client>
Address = 10.0.0.2/24
DNS = 8.8.8.8
DNS = 10.0.0.1

[Peer]
PublicKey = <clau_publica_servidor>
Endpoint = <ip_publica_servidor>:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25

# Habilita WireGuard i reinicia el servei
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0

# Si es produeix algun error pot ser perquè s'ha de instal·lar resolvconf
# És important respectar l'ordre perquè sinó no funcionarà.

sudo nano /etc/resolv.conf
nameserver 10.0.0.1
sudo chattr +i /etc/resolv.conf
sudo ip route add default via 10.0.0.1 dev wg0
sudo systemctl restart systemd-resolved
