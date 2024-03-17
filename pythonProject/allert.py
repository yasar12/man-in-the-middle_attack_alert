
import socket
import csv
import subprocess
import ctypes
import time
print("MAN IN THE MIDDLE ATTACK DETECTION TOOL")

# Get ARP table

wlanapi = ctypes.windll.wlanapi
wlan = ctypes.windll.wlanui

def disconnect_from_network():
    try:
        # ipconfig komutunu kullanarak internet bağlantısını kesme
        subprocess.run(["ipconfig", "/release"], check=True)
        print("Internet bağlantısı başarıyla kesildi.")
    except subprocess.CalledProcessError as e:
        print("Hata:", e)


def get_arp_table(IP):
    cmd = "arp -a"
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None, shell=True)
    output, _ = process.communicate()
    output = output.decode("utf-8")  # Decode the bytes-like object to a string
    interfaceBlocks = output.split('Interface:')

    for interfaceBlock in interfaceBlocks:
        lines = interfaceBlock.split('\r\n')
        interfaceIP = lines[0].split('---')[0].strip()

        if interfaceIP == IP:
            names = ['Internet Address', 'Physical Address', 'Type']
            reader = csv.DictReader(
                lines[1:], fieldnames=names, skipinitialspace=True, delimiter=' ')
            next(reader)

            return [block for block in reader]

    # Eğer belirtilen IP için ARP tablosu bulunamazsa None döndür
    return None


# Get IP Address
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

mitm = False
while not mitm:
    IP = get_ip()

    arp_table = get_arp_table(IP)
    if arp_table is None or len(arp_table) == 0:
        print("ARP tablosu alınamadı veya boş.")
        time.sleep(2)
        continue  # Sonraki döngü adımına geç

    mac_address = arp_table[0]['Physical Address']


    print("Gateway's MAC Address is ", mac_address, "\r\n")

    print("Looking for MITM")
    for line in arp_table[1:]:
        if line['Physical Address'] == mac_address:
            mitm = True

    if mitm:
        print("MITM Attack is Detected for your safety we disconnected your internet connection, please contact your internet service distrubuter.")
        print("Until you close the program you can't gain your internet connection")
        while True:
            disconnect_from_network()
            time.sleep(0.2)

    else:
        print("No MITM Attack Right Now")
    time.sleep(4)
