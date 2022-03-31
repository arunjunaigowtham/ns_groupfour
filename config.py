import os
import sys
import re

list_jails = ["ssh","wordpress", "php", "joomla"]

log_paths = { "ssh" : "" , "wordpress" : "", "php" : "", "joomla" : ""}
regexs = { "ssh" : "", "wordpress" : "", "php" : "", "joomla" : ""}

def main():
	args = sys.argv
	check_args(args)
	global jailname
	jailname = args[1]
	global bantime
	bantime = args[2]
	global maxretry
	maxretry = args[3]
	global failurewindow
	failurewindow = args[4]
	update_fields(jailname)
	
def check_args(args):
	args= sys.argv
	if(len(args) < 5 or not args[2].isnumeric() or not args[3].isnumeric() or not args[4].isnumeric()):
		print("ERROR, please use the following format : [JAILNAME] [BANTIME] [MAXRETRY] [FAILUREWINDOW]")
		return
	if(args[1].lower() not in list_jails):
		print("Please enter a jail name from the following: ssh, wordpress, php, joomla")
		return


def update_fields(name):
	name_brackets = "[" + name + "]"
	print(name_brackets)

	with open("jail.local", 'r') as f:
    		lines = f.readlines()

	in_the_jail = False
	with open("jail.local", 'w') as f:

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
	with open("jail.local", 'a') as f:
		f.write("\n")
		f.write("\n")
		f.write(name_brackets)
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
main()				
