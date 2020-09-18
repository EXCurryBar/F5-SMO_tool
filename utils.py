import socket
import datetime
import matplotlib.pyplot as plt
import time
import paramiko
import requests
from scp import SCPClient
from numpy import shape
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from time import sleep
from os import system

hostname = ""
now = datetime.datetime.now().strftime("%Y%m%d")
requests.packages.urllib3.disable_warnings()


def usage(img):  # return the maxium and minium of a graph
    img = plt.imread(img)
    point1 = []
    point2 = []
    x, y = shape(img)[0:2]

    for i in range(x):
        for j in range(y):
            if sum(img[i, j][0:3]) == 3:
                point1 = [i, j]
                break
    for i in range(x-1, 0, -1):
        for j in range(y-1, 0, -1):
            if sum(img[i, j][0:3]) == 3:
                point2 = [i, j]
                break

    img = img[point2[0]:point1[0], point1[1]:point2[1]]
    x, y = shape(img)[0:2]
    for i in range(x):
        for j in range(y):
            if sum(img[i, j][0:3]) == 0:
                (Max) = i
                break
    for i in range(x-1, 0, -1):
        for j in range(y-1, 0, -1):
            if sum(img[i, j][0:3]) == 0:
                Min = i
                break
    if (Max) == Min:
        return str(int((x-Max) * 100 / x)) + '%'
    else:
        return str(int((x-Max) * 100 / x)) + "% ~ " + str(int((x-Min) * 100 / x)) + '%'


def is_avail(IP, port=22):  # return True if device is reachable
    try:
        host = socket.gethostbyname(IP)
        s = socket.create_connection((host, port), 2)
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


def get_data(IP, ACC, PASS): # get MEM and CPU usage
    name_lst = ["mem", "cpu"]
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')

    driver = webdriver.Chrome(chrome_options=options)
    driver.get("https://" + IP + "/tmui/login.jsp")
    driver.find_element_by_id("username").send_keys(ACC)
    driver.find_element_by_id("passwd").send_keys(PASS)
    driver.find_element_by_xpath("//button[1]").click()
    # add login fail check
    driver.get("https://" + IP +
               "/tmui/Control/jspmap/tmui/system/stats/list.jsp?subset=All")
    sleep(5)
    driver.switch_to.frame(driver.find_element_by_id("contentframe"))
    s = Select(driver.find_element_by_name("int_select"))
    s.select_by_value("3")

    img = driver.find_elements_by_tag_name("img")
    img_lst = [item.get_attribute(
        'src') for item in img if item.get_attribute('src')[-3:] == "png"]

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    }
    s = requests.session()
    s.headers.update(headers)
    for cookie in driver.get_cookies():
        c = {cookie['name']: cookie['value']}
        s.cookies.update(c)
    driver.close()
    for i in range(2):
        r = s.get(img_lst[i], allow_redirects=True, verify=False)
        open(name_lst[i] + '.png', 'wb').write(r.content)
    res = []

    for name in name_lst:
        res.append([name, usage(name + ".png")])

    [system("del " + name + ".png") for name in name_lst]
    
    return res
