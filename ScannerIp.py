#!/usr/bin/env python3

import subprocess
import sys
import re

# Definir colores
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
RESET = '\033[0m'

def print_colored(message, color):
    """Imprime mensajes con el color especificado."""
    print(f"{color}{message}{RESET}")

def ping_ip(ip):
    """Hace un ping a la IP para verificar si está activa."""
    print_colored(f"Haciendo ping a la IP: {ip}...", BLUE)
    try:
        # Ejecuta el comando ping con -c 4 para enviar 4 paquetes ICMP
        response = subprocess.run(['ping', '-c', '4', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if response.returncode == 0:
            print_colored(f"La IP {ip} está activa. Procediendo con el escaneo de puertos...", GREEN)
            return True
        else:
            print_colored(f"La IP {ip} no está accesible. No se puede continuar con el escaneo.", RED)
            return False
    except Exception as e:
        print_colored(f"Error al hacer ping a la IP: {e}", RED)
        return False

def scan_open_ports(ip):
    """Escanea los puertos abiertos usando nmap."""
    print_colored("Escaneando puertos abiertos...", BLUE)
    try:
        # Ejecuta el comando nmap para escanear todos los puertos abiertos
        result = subprocess.run(['nmap', '-sS', '-n', '-Pn', '-vvv', '--min-rate', '5000', '-p-', '--open', ip],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Filtra los puertos abiertos usando una expresión regular
        open_ports = re.findall(r'(\d+/tcp)\s+open', result.stdout)
        
        if open_ports:
            print_colored(f"Puertos abiertos encontrados: {', '.join(open_ports)}", GREEN)
            # Guardamos los puertos abiertos en un archivo
            with open('OpenPorts.txt', 'w') as file:
                for port in open_ports:
                    file.write(port + '\n')
            return [port.split('/')[0] for port in open_ports]
        else:
            print_colored(f"No se encontraron puertos abiertos en {ip}.", YELLOW)
            return []
    except Exception as e:
        print_colored(f"Error al escanear los puertos: {e}", RED)
        return []

def detailed_scan(ip, open_ports):
    """Realiza un escaneo detallado sobre los puertos abiertos."""
    if not open_ports:
        print_colored("No hay puertos abiertos para escanear detalladamente.", YELLOW)
        return
    
    ports = ','.join(open_ports)  # Convierte la lista de puertos a una cadena separada por comas
    print_colored(f"Ejecutando escaneo detallado con -sC -sV sobre los puertos {ports}...", BLUE)
    try:
        # Ejecuta el escaneo detallado con -sC (scripts predeterminados) y -sV (versiones de servicios)
        result = subprocess.run(['nmap', '-sC', '-sV', '-v', '-p', ports, ip],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print_colored(result.stdout, GREEN)
    except Exception as e:
        print_colored(f"Error al realizar el escaneo detallado: {e}", RED)

def main():
    if len(sys.argv) != 2:
        print_colored("Uso: python3 script.py <IP>", YELLOW)
        sys.exit(1)
    
    ip = sys.argv[1]

    # Primero, hacer un ping a la IP para verificar si está activa
    if ping_ip(ip):
        # Escanear los puertos abiertos
        open_ports = scan_open_ports(ip)
        
        # Si hay puertos abiertos, realizar el escaneo detallado
        detailed_scan(ip, open_ports)

if __name__ == "__main__":
    main()
