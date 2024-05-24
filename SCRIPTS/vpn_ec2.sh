#!/bin/bash

# S'ha de obrir el port UDP 51820 al security group de la instància
# Actualitza els paquets i instal·la WireGuard
sudo apt update
sudo apt install wireguard -y

# Genera claus per al servidor
wg genkey | tee privatekey | wg pubkey > publickey

# Per veure les claus
cat privatekey
cat publickey

# Crea l'arxiu de configuració de WireGuard
sudo nano /etc/wireguard/wg0.conf
[Interface]
PrivateKey = <clau_privada_servidor>
Address = 10.0.0.1/24
ListenPort = 51820

[Peer]
PublicKey = <clau_publica_client>
AllowedIPs = 10.0.0.2/32

# Habilita l'enrutament i reenviament de paquets
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -p

# Configura iptables per enrutar tràfic
sudo iptables -A FORWARD -i wg0 -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables-save | sudo tee /etc/iptables/rules.v4

# Habilita WireGuard i reinicia el servei
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0

# És important respectar l'ordre perquè sinó no funcionarà.
# Si no funciona bé, tornar a executar: 
sudo iptables -A FORWARD -i wg0 -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables-save | sudo tee /etc/iptables/rules.v4
