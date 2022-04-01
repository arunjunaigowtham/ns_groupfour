from cmath import e
import os
import sys
import time
import datetime
import subprocess
import threading
import re
import configparser as ConfigParser


def remove_iptables_rule(ip_address):
    subprocess.call(['iptables','-D','INPUT','-s',ip_address,'-j','DROP'])
    print('[+] IP address {} removed from iptables'.format(ip_address))

def ban_ip_thread(kill, jail_name, bantime, maxretry, failurewindow, log_path, failure_regex):
    # check if the sudo permission is given
    if os.geteuid() != 0:
        print("[!] Please run this script as root")
        exit(1)
    # # Input configuration
    # jail_name = 'wordpress'
    # failure_regex = re.compile(r'^(?=.*\swordpress\b)(?=.*\bAuthentication failure\b).*$')
    # log_path = '/var/log/auth.log'
    # failurewindow = 300
    # maxretry = 3
    # bantime = 60
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
            print(line)
            # Get the IP address of the failed login attempt
            if jail_name == 'wordpress':
                # Get all the occurences of the IP address in the line and save 2nd occurence
                ip = re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', line)[1]
            else:
                ip = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', line).group(0)
            print(ip)
            if ip not in ip_ban_dict:
                ip_ban_dict[ip] = 1
                ip_start_time_dict[ip]  = re.search(r'\w{3}\s+(\d{1}|\d{2}) \d{2}:\d{2}:\d{2}', line).group(0)
            else:
                ip_ban_dict[ip] += 1
            print(ip_ban_dict)
            # Check if the IP address has exceeded the maximum number of failed login attempts
            if ip_ban_dict[ip] >= maxretry:
                ip_end_time_dict[ip] = re.search(r'\w{3}\s+(\d{1}|\d{2}) \d{2}:\d{2}:\d{2}', line).group(0)
                diff = datetime.datetime.strptime(ip_end_time_dict[ip], '%b %d %H:%M:%S') - datetime.datetime.strptime(ip_start_time_dict[ip], '%b %d %H:%M:%S')

                print(ip_start_time_dict[ip], ip_end_time_dict[ip])
                print(diff)
                # Check if the time difference between the failed login attempts is less than the failure window
                if diff.seconds <= failurewindow:
                    # Remove the ip from the dictionary
                    del ip_ban_dict[ip]
                    del ip_start_time_dict[ip]
                    del ip_end_time_dict[ip]
                    # Check for the IP address in the iptables list
                    # If it is not in the list, ban the IP address
                    # If it is in the list, do nothing
                    if not re.search(ip,subprocess.check_output(['iptables','-S']).decode('utf-8')):
                        subprocess.call(['iptables','-I','INPUT','-s',ip,'-j','DROP'])
                        print('[+] IP address {} banned'.format(ip))
                        threading.Timer(bantime, remove_iptables_rule, [ip]).start()
                    print(ip_ban_dict)
                    print(ip_start_time_dict)
                    print(ip_end_time_dict)
        else:
            print('No match')

if __name__ == '__main__':
    try :
        while True:
            cp = ConfigParser.RawConfigParser()
            cp.read('custom_jail.conf')
            services = cp.sections()
            for service in services:
                print(service)
                bantime = cp.getint(service, 'bantime')
                print(bantime)
                maxretry = cp.getint(service, 'maxretry')
                print(maxretry)
                failurewindow = cp.getint(service, 'failurewindow')
                print(failurewindow)
                failure_regex = cp.get(service, 'regex')
                print(failure_regex)
                logpath = cp.get(service, 'logpath')
                print(logpath)
                enabled = cp.getboolean(service, 'enabled')
                print(enabled)
                if service == 'ssh':
                    if enabled:
                        print('[+] SSH jail enabled')
                        if 'ssh_jail' in locals():
                            if ssh_jail.is_alive():
                                print('[+] SSH jail already running')
                        else:
                            kill = False
                            ssh_jail = threading.Thread(target=ban_ip_thread, args=(lambda: kill, 'ssh', bantime, maxretry, failurewindow, logpath, failure_regex))
                            ssh_jail.start()
                    else:
                        print('[-] SSH jail disabled')
                        # Kill the ssh thread if its running
                        if 'ssh_jail' in locals():
                            if ssh_jail.is_alive():
                                kill = True
                                ssh_jail.join()
                if service == 'wordpress':
                    if enabled:
                        print('[+] Wordpress jail enabled')
                        if 'wordpress_jail' in locals():
                            if wordpress_jail.is_alive():
                                print('[+] Wordpress jail already running')
                        else:
                            kill = False
                            wordpress_jail = threading.Thread(target=ban_ip_thread, args=(lambda: kill, 'wordpress', bantime, maxretry, failurewindow, logpath, failure_regex))
                            wordpress_jail.start()
                    else:
                        print('[-] Wordpress jail disabled')
                        # Kill the wordpress thread if its running
                        if 'wordpress_jail' in locals():
                            if wordpress_jail.is_alive():
                                kill = True
                                wordpress_jail.join()
                if service == 'phpmyadmin':
                    if enabled:
                        print('[+] Phpmyadmin jail enabled')
                        if 'phpmyadmin_jail' in locals():
                            if phpmyadmin_jail.is_alive():
                                print('[+] Phpmyadmin jail already running')
                        else:
                            kill = False
                            phpmyadmin_jail = threading.Thread(target=ban_ip_thread, args=(lambda: kill, 'phpmyadmin', bantime, maxretry, failurewindow, logpath, failure_regex))
                            phpmyadmin_jail.start()
                    else:
                        print('[-] Phpmyadmin jail disabled')
                        # Kill the phpmyadmin thread if its running
                        if 'phpmyadmin_jail' in locals():
                            if phpmyadmin_jail.is_alive():
                                kill = True
                                phpmyadmin_jail.join()
                if service == 'joomla':
                    if enabled:
                        print('[+] Joomla jail enabled')
                        if 'joomla_jail' in locals():
                            if joomla_jail.is_alive():
                                print('[+] Joomla jail already running')
                        else:
                            kill = False
                            joomla_jail = threading.Thread(target=ban_ip_thread, args=(lambda: kill, 'joomla', bantime, maxretry, failurewindow, logpath, failure_regex))
                            joomla_jail.start()
                    else:
                        print('[-] Joomla jail disabled')
                        # Kill the joomla thread if its running
                        if 'joomla_jail' in locals():
                            if joomla_jail.is_alive():
                                kill = True
                                joomla_jail.join()
            time.sleep(2)
    except Exception as e:
        print(e.args)