from flask import Flask, render_template, redirect, request
import requests
import sys, os
import json
import configparser as ConfigParser
import time
import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

secure_admin_main_file = 'secure_admin_run.py'  # Name of the main file
config_file = 'secure_admin_config.py'  # Name of the config file
log_file = 'custom_jail.conf'  # Name of the log file


@app.route('/')
def secret_view():
    return redirect('/home', code=302)


##############################
# Home page                #
##############################

@app.route('/home', methods=['GET', 'POST'])
def home():
    # status = fail2banStatus()
    return render_template('index.html')


@app.route('/start', methods=['GET', 'POST'])
def start():
    f = os.popen(f'python3 {config_file} ssh false 30 3 300')       # Configure the SSH service
    time.sleep(1)
    f = os.popen(f'python3 {config_file} joomla false 30 3 300')       # Configure the Joomla service
    time.sleep(1)
    f = os.popen(f'python3 {config_file} wordpress false 30 3 300')       # Configure the Wordpress service
    time.sleep(1)
    f = os.popen(f'python3 {config_file} phpmyadmin false 30 3 300')        # Configure the Phpmyadmin service
    time.sleep(1)
    s = os.popen(f'python3 {secure_admin_main_file}')      # Start the Main process
    time.sleep(1)
    return redirect("/", code=302)


@app.route('/stop', methods=['GET', 'POST'])
def stop():
    # get pid of the process
    pid = os.popen(f'pgrep -f {secure_admin_main_file}').read()
    # kill the process
    os.popen(f'kill -9 {pid}')
    return redirect("/", code=302)


##############################
# Config page                #
##############################


@app.route('/config/input/<s>', methods=["GET", "POST"])
def read_request(s):
    if request.method == 'POST':
        maxretry = request.form.get('maxretry')
        bantime = request.form.get('bantime')
        failurewindow = request.form.get('failurewindow')
        print(maxretry, bantime, failurewindow)
        cp = ConfigParser.RawConfigParser()
        cp.read(log_file)
        cp.set(s, 'maxretry', maxretry)
        cp.set(s, 'bantime', bantime)
        cp.set(s, 'failurewindow', failurewindow)
        with open(log_file, 'w') as configfile:
            cp.write(configfile)
        return redirect("/config", code=302)


@app.route('/config', methods=['GET', 'POST'])
def config():
    cp = ConfigParser.RawConfigParser()
    cp.read(log_file)
    services = cp.sections()
    # services = ['ssh', 'joomla', 'wordpress', 'phpmyadmin']
    print(services)
    return render_template('config.html', cp=cp, services=services)


@app.route('/enable/<s>', methods=['GET', 'POST'])
def enable(s=None):
    cp = ConfigParser.RawConfigParser()
    # if log file does not exist, create it

    cp.read(log_file)
    cp.set(s, 'enabled', 'true')
    with open(log_file, 'w') as configfile:
        cp.write(configfile)
    return redirect("/config", code=302)


@app.route('/disable/<s>', methods=['GET', 'POST'])
def disable(s=None):
    cp = ConfigParser.RawConfigParser()
    cp.read(log_file)
    cp.set(s, 'enabled', 'false')
    with open(log_file, 'w') as configfile:
        cp.write(configfile)
    return redirect("/config", code=302)



# ##############################
# # Banned IP                  #
# ##############################
#
# def getcountry(ip):
# 	r = requests.get('http://ip-api.com/json/'+ip)
# 	parsed_json=r.json()
# 	return parsed_json
#
# @app.route('/banned', methods=['GET', 'POST'])
# @basic_auth.required
# def banned():
#   f = os.popen("cat /var/log/fail2ban.log | grep Ban | awk '{print $7}'")
#   banned = f.read()
#
#
#   theFile = open('/var/log/fail2ban.log','r')
#   FILE = theFile.readlines()
#   theFile.close()
#   printList = []
#   for line in FILE:
#     if ('Ban' in line):
#       printList.append(line)
#   return render_template('banned.html', printList = printList, getcountry=getcountry)
# @app.route('/banned', methods=['GET', 'POST'])
# @basic_auth.required
# def banned():
#     # get banned ip list from iptables
#     f = os.popen("iptables -L -n | grep 'DROP' | awk '{print $4}'")
#     banned = f.read()
#     print(banned)
#     return render_template('banned.html', banned=banned)


##############################
# App launcher               #
##############################

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1')
