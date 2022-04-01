from cmath import e
import os
import sys
import time
import datetime
import subprocess
import threading
import multiprocessing
import re
import configparser as ConfigParser

def remove_iptables_rule(ip_address):
    subprocess.call(['iptables','-D','INPUT','-s',ip_address,'-j','DROP'])

def ban_ip_thread(jail_name, bantime, maxretry, failurewindow, log_path, failure_regex):
    # check if the sudo permission is given
    if os.geteuid() != 0:
        print("[!] Please run this script as root")
        exit(1)
    failure_regex = re.compile(failure_regex)
    # Dictionary of ip addresses and their failure counts
    ip_ban_dict = {}
    ip_start_time_dict = {}
    ip_end_time_dict = {}

    f = subprocess.Popen(['tail','-F', '-n', '1', log_path],\
            stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    while True:
        if kill():
            break
        line = f.stdout.readline().decode('utf-8')
        # Check for regex match for failed login attempts
        if failure_regex.search(line):

            # Get the IP address of the failed login attempt
            if jail_name == 'wordpress':
                # Get all the occurences of the IP address in the line and save 2nd occurence
                ip = re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', line)[1]
            else:
                ip = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', line).group(0)

            if ip not in ip_ban_dict:
                ip_ban_dict[ip] = 1
                if jail_name == 'joomla':
                    ip_start_time_dict[ip] = line.split(" ")[0].split("+")[0]
                else:
                    ip_start_time_dict[ip]  = re.search(r'\w{3}\s+(\d{1}|\d{2}) \d{2}:\d{2}:\d{2}', line).group(0)
            else:
                ip_ban_dict[ip] += 1

            # Check if the IP address has exceeded the maximum number of failed login attempts
            if ip_ban_dict[ip] >= maxretry:
                if jail_name == 'joomla':
                    ip_end_time_dict[ip] = line.split(" ")[0].split("+")[0]
                    diff = datetime.datetime.strptime(ip_end_time_dict[ip], '%Y-%m-%dT%H:%M:%S') - datetime.datetime.strptime(ip_start_time_dict[ip], '%Y-%m-%dT%H:%M:%S')
                else:
                    ip_end_time_dict[ip] = re.search(r'\w{3}\s+(\d{1}|\d{2}) \d{2}:\d{2}:\d{2}', line).group(0)
                    diff = datetime.datetime.strptime(ip_end_time_dict[ip], '%b %d %H:%M:%S') - datetime.datetime.strptime(ip_start_time_dict[ip], '%b %d %H:%M:%S')

                # Check if the time difference between the failed login attempts is less than the failure window
                if diff.seconds <= failurewindow:
                    # Check for the IP address in the iptables list
                    # If it is not in the list, ban the IP address
                    # If it is in the list, do nothing
                    if not re.search(ip,subprocess.check_output(['iptables','-S']).decode('utf-8')):
                        subprocess.call(['iptables','-I','INPUT','-s',ip,'-j','DROP'])
                        threading.Timer(bantime, remove_iptables_rule, [ip]).start()

                # Remove the ip from the dictionary
                del ip_ban_dict[ip]
                del ip_start_time_dict[ip]
                del ip_end_time_dict[ip]

if __name__ == '__main__':
    try :
        while True:
            cp = ConfigParser.RawConfigParser()
            cp.read('custom_jail.conf')
            jails = cp.sections()
            for jail in jails:
                print(jail)
                bantime = cp.getint(jail, 'bantime')
                print(bantime)
                maxretry = cp.getint(jail, 'maxretry')
                print(maxretry)
                failurewindow = cp.getint(jail, 'failurewindow')
                print(failurewindow)
                failure_regex = cp.get(jail, 'regex')
                print(failure_regex)
                logpath = cp.get(jail, 'logpath')
                print(logpath)
                enabled = cp.getboolean(jail, 'enabled')
                print(enabled)

                # Start/Stop the thread for each jail
                if jail == 'ssh':
                    if enabled:
                        print('[+] SSH jail enabled')
                        if 'ssh_jail' in locals():
                            if ssh_jail.is_alive():
                                print('[+] SSH jail already running')
                        else:
                            ssh_jail = multiprocessing.Process(target=ban_ip_thread, args=('ssh', bantime, maxretry, failurewindow, logpath, failure_regex))
                            ssh_jail.start()
                    else:
                        print('[-] SSH jail disabled')
                        # Kill the ssh thread if its running
                        if 'ssh_jail' in locals():
                            if ssh_jail.is_alive():
                                ssh_jail.terminate()
                if jail == 'wordpress':
                    if enabled:
                        print('[+] Wordpress jail enabled')
                        if 'wordpress_jail' in locals():
                            if wordpress_jail.is_alive():
                                print('[+] Wordpress jail already running')
                        else:
                            wordpress_jail = multiprocessing.Process(target=ban_ip_thread, args=('wordpress', bantime, maxretry, failurewindow, logpath, failure_regex))
                            wordpress_jail.start()
                    else:
                        print('[-] Wordpress jail disabled')
                        # Kill the wordpress thread if its running
                        if 'wordpress_jail' in locals():
                            if wordpress_jail.is_alive():
                                wordpress_jail.terminate()
                if jail == 'phpmyadmin':
                    if enabled:
                        print('[+] Phpmyadmin jail enabled')
                        if 'phpmyadmin_jail' in locals():
                            if phpmyadmin_jail.is_alive():
                                print('[+] Phpmyadmin jail already running')
                        else:
                            phpmyadmin_jail = multiprocessing.Process(target=ban_ip_thread, args=('phpmyadmin', bantime, maxretry, failurewindow, logpath, failure_regex))
                            phpmyadmin_jail.start()
                    else:
                        print('[-] Phpmyadmin jail disabled')
                        # Kill the phpmyadmin thread if its running
                        if 'phpmyadmin_jail' in locals():
                            if phpmyadmin_jail.is_alive():
                                phpmyadmin_jail.terminate()
                if jail == 'joomla':
                    if enabled:
                        print('[+] Joomla jail enabled')
                        if 'joomla_jail' in locals():
                            if joomla_jail.is_alive():
                                print('[+] Joomla jail already running')
                        else:
                            joomla_jail = multiprocessing.Process(target=ban_ip_thread, args=('joomla', bantime, maxretry, failurewindow, logpath, failure_regex))
                            joomla_jail.start()
                    else:
                        print('[-] Joomla jail disabled')
                        # Kill the joomla thread if its running
                        if 'joomla_jail' in locals():
                            if joomla_jail.is_alive():
                                joomla_jail.terminate()
            time.sleep(2)
    except Exception as e:
        print(e.args)