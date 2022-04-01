import sys
import os
import configparser as cp

list_jails = ["ssh", "wordpress", "phpmyadmin", "joomla"]

log_paths = {"ssh": r'/var/log/auth.log',
             "wordpress": r'/var/log/auth.log',
             "phpmyadmin": r'/var/log/auth.log',
             "joomla": r'/var/www/html/joomla/administrator/logs/error.php'}
regexs = {"ssh": r'^(?=.*\ssshd\b)(?=.*\bFailed password\b).*$',
          "wordpress": r'^(?=.*\swordpress\b)(?=.*\bAuthentication failure\b).*$',
          "phpmyadmin": r'^(?=.*\sphpMyAdmin\b)(?=.*\buser denied\b).*$',
          "joomla": r'^(?=.*\sjoomlafailure\b).*$'}
config_file = 'custom_jail.conf'


def main_fn():
    args = sys.argv
    print(args)
    check_args(args)
    global jailname
    jailname = args[1]
    global enable
    enable = args[2]
    global bantime
    bantime = args[3]
    global maxretry
    maxretry = args[4]
    global failurewindow
    failurewindow = args[5]
    update_fields(jailname)
    return


def check_args(args):
    if (len(args) < 6 or not args[3].isnumeric() or not args[4].isnumeric() or not args[5].isnumeric()):
        print(
            "ERROR, please use the following format : [JAILNAME] [ENABLED:true/false] [BANTIME] [MAXRETRY] [FAILUREWINDOW]")
        sys.exit(1)
    if (args[1].lower() not in list_jails):
        print("Please enter a jail name from the following: ssh, wordpress, phpmyadmin, joomla")
        sys.exit(1)


def update_fields(jailname):
    config = cp.RawConfigParser()
    config.read(config_file)
    if jailname not in config.sections():
        config.add_section(jailname)
    config.set(jailname, 'enabled', enable)
    config.set(jailname, 'bantime', bantime)
    config.set(jailname, 'maxretry', maxretry)
    config.set(jailname, 'failurewindow', failurewindow)
    config.set(jailname, 'bantime_old', bantime)
    config.set(jailname, 'maxretry_old', maxretry)
    config.set(jailname, 'failurewindow_old', failurewindow)
    config.set(jailname, 'logpath', log_paths[jailname])
    config.set(jailname, 'regex', regexs[jailname])
    with open(config_file, 'w') as configfile:
        config.write(configfile)


main_fn()
