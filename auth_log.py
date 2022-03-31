import os
import sys
import time
import datetime
import subprocess
import threading
import re


def remove_iptables_rule(ip_address):
    subprocess.call(['iptables','-D','INPUT','-s',ip_address,'-j','DROP'])
    print('[+] IP address {} removed from iptables'.format(ip_address))

def main():
    # Input configuration
    failure_regex = re.compile(r'Failed password')
    log_path = '/var/log/auth.log'
    failurewindow = 300
    maxretry = 5
    bantime = 60

    # Dictionary of ip addresses and their failure counts
    ip_ban_dict = {}
    ip_start_time_dict = {}
    ip_end_time_dict = {}

    f = subprocess.Popen(['tail','-F', '-n', '1', log_path],\
            stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    while True:
        line = f.stdout.readline().decode('utf-8')
        # Check for regex match for failed login attempts
        if failure_regex.search(line):
            print(line)
            # Get the IP address of the failed login attempt
            ip = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',line).group(0)
            print(ip)
            if ip not in ip_ban_dict:
                ip_ban_dict[ip] = 1
                ip_start_time_dict[ip]  = re.search(r'\w{3} \d{2} \d{2}:\d{2}:\d{2}', line).group(0)
            else:
                ip_ban_dict[ip] += 1
            print(ip_ban_dict)
            # Check if the IP address has exceeded the maximum number of failed login attempts
            if ip_ban_dict[ip] >= maxretry:
                ip_end_time_dict[ip] = re.search(r'\w{3} \d{2} \d{2}:\d{2}:\d{2}', line).group(0)
                diff = datetime.datetime.strptime(ip_end_time_dict[ip], '%b %d %H:%M:%S') - datetime.datetime.strptime(ip_start_time_dict[ip], '%b %d %H:%M:%S')

                print(ip_start_time_dict[ip], ip_end_time_dict[ip])
                print(diff)
                # Check if the time difference between the failed login attempts is less than 5 minutes
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

if __name__ == '__main__':
    main()