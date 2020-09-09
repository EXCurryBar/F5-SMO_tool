import socket
import datetime
import matplotlib.pyplot as plt
import time
import paramiko
from scp import SCPClient

hostname = ""
now = datetime.datetime.now().strftime("%Y%m%d")


def usage(img):  # return the maxium and minium of a graph
    img = plt.imread(img)
    img = img[21:121, 67:605]

    for i in range(0, 100, 1):
        for j in range(0, 538, 1):
            if sum(img[i, j][0:2]) == 0:
                Max = 100 - i
                break
        else:
            continue
        break

    for i in range(99, 0, -1):
        for j in range(537, 0, -1):
            if sum(img[i, j][0:2]) == 0:
                Min = 100 - i
                break
        else:
            continue
        break
    if Max == Min:
        return str(Max) + '%'
    else:
        return str(Min) + "% ~ " + str(Max) + '%'


def is_avail(IP):  # return True if device is reachable
    try:
        host = socket.gethostbyname(IP)
        s = socket.create_connection((host, 22), 2)
        return True
    except:
        pass
    return False


def get_qkview(client):  # generate qkview and saved at C:\qkview
    try:
        stdin, stdout, stderr = client.exec_command(
            "qkview;mv /var/tmp/"+hostname+".qkview /var/tmp/" + now + "_" + hostname + ".qkview")
        idk = stdout.readlines()

        scp = SCPClient(client.get_transport())
        scp.get("/shared/tmp/" + hostname + "_" + now + ".qkview", "\\qkviews")
        print("Qkview saved")
        # return "OK"
    except:
        print("Error occur")
        # return "Error"


def get_ucs(client):  # generate ucs and saved at C:\ucs
    try:
        stdin, stdout, stderr = client.exec_command(
            "tmsh save /sys ucs /var/local/ucs/" + hostname + '_' + now + ".ucs")
        idk = stdout.readlines()

        scp = SCPClient(client.get_transport())
        scp.get("/var/local/ucs/" + hostname + "_" + now + ".ucs", "\\ucs")
        print("UCS saved")
        # return "OK"
    except:
        print("Error occur")
        # return "Error"
