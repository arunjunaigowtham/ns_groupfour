import os
from sqlite3 import enable_shared_cache
import sys
import re

list_jails = ["ssh","wordpress", "php", "joomla"]

log_paths = { "ssh" : r'/var/log/auth.log',
			  "wordpress" : r'/var/log/auth.log',
			  "php" : r'/var/log/auth.log',
			  "joomla" : r''}
regexs = { "ssh" : r'^(?=.*\ssshd\b)(?=.*\bFailed password\b).*$',
		   "wordpress" : r'^(?=.*\swordpress\b)(?=.*\bAuthentication failure\b).*$',
		   "php" : r'^(?=.*\sphpMyAdmin\b)(?=.*\buser denied\b).*$',
		   "joomla" : r''}
config_file = 'custom_jail.conf'

def main():
	args = sys.argv
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
	
def check_args(args):
	args= sys.argv
	if(len(args) < 6 or not args[3].isnumeric() or not args[4].isnumeric() or not args[5].isnumeric()):
		print("ERROR, please use the following format : [JAILNAME] [ENABLED:true/false] [BANTIME] [MAXRETRY] [FAILUREWINDOW]")
		return
	if(args[1].lower() not in list_jails):
		print("Please enter a jail name from the following: ssh, wordpress, php, joomla")
		return


def update_fields(name):
	name_brackets = "[" + name + "]"
	print(name_brackets)

	with open(config_file, 'w+') as f:
		lines = f.readlines()

	in_the_jail = False
	with open(config_file, 'w+') as f:
		for line in lines:
			if (name_brackets in line and "#" not in line):
				print(line)
				in_the_jail = True
		
			elif(in_the_jail == False):
				
				f.write(line)
			elif(line[0] == "[" and line[-2] == "]"):
				in_the_jail = False
				f.write(line)
			else:
				print(line)
	with open(config_file, 'a') as f:
		f.write("\n")
		f.write("\n")
		f.write(name_brackets)
		f.write("\n")
		f.write("enabled = ")
		f.write(enable)
		f.write("\n")
		f.write("bantime = ")	
		f.write(str(bantime))
		f.write("\n")	
		f.write("maxretry = ")	
		f.write(str(maxretry))
		f.write("\n")		
		f.write("failurewindow = ")	
		f.write(str(failurewindow))
		f.write("\n")
		f.write("logpath = ")
		f.write(str(log_paths[name]))
		f.write("\n")
		f.write("regex = ")
		f.write(str(regexs[name]))
main()				
