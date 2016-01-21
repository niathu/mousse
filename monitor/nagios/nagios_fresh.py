#!/usr/bin/python
import os,sys,yaml
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('env',help="this is env variable,such as zckd,onecloud and so on.")
args=parser.parse_args()

Linux_Host_Use="linux-server"
Linux_Service_Use="1min-service"
Win_Host_Use="windows-server"
Win_Service_Use="5min-windows"
Service_Use=Linux_Service_Use
Linux_Host_Passive_Use="passive-linux"
Windows_Host_Passive_Use="passive-win"
Passive_Service_Use="passive-service"

ip_file="ip.yaml"
windows_file="windows.yaml"
ingredient_file="ingredient.yaml"
check_file="check.yaml"
env=args.env
active_file="active_"+env+".cfg"
passive_file="passive_"+env+".cfg"

ip_to_ingredient=yaml.load(open(ip_file))
windows_hosts=yaml.load(open(windows_file))
ingredient_to_ip={}

#cmd_file="check_cmd.txt"
#check_file="check_file.txt"
#conn=MySQLdb.connect(host="127.0.0.1",port=3306,user='clouder',passwd='engine',db='mycmdb')
#cmd={}
#cur=conn.cursor()
#cur.execute('select * from nagioscheck')
#for x in cur:
#    cmd[x[1]]=x[4]
#cur.execute('select b.name,c.checkName from ingredientcheck a,ingredientdefine b,nagioscheck c where a.ingredientDefineId=b.id and a.checkId=c.id order by 1')
#check={}
#for y in cur:
#    if y[0] not in check:check[y[0]]=[]
#    check[y[0]].append(y[1])
#
#with open(cmd_file,'w') as fn:
#   fn.write(yaml.dump(cmd))
#with open(check_file,'w') as fn:
#    fn.write(yaml.dump(check))   

for ip in ip_to_ingredient:
	for ingredient in ip_to_ingredient[ip]:
		if ingredient not in ingredient_to_ip.keys():
			ingredient_to_ip[ingredient]=set()
		ingredient_to_ip[ingredient].add(ip)

with open(active_file,'w') as fn:
	for ip in ip_to_ingredient:
		use="windows-server" if ip in windows_hosts['windows'] else "linux-server"
		host_info="define host {\n\tuse\t%s\n\thost_name\t%s\n\talias\t%s\n\taddress\t%s\n\t}\n"%(use,env+'_'+ip,env+'_'+ip,ip)
		fn.write(host_info)
	for ingredient in ingredient_to_ip:
		ingredient_info="define hostgroup {\n\thostgroup_name\t%s\n\talias\t%s\n\tmembers\t%s\n\t}\n"%(env+'_'+ingredient,env+'_'+ingredient,','.join([env+'_'+ip for ip in ingredient_to_ip[ingredient]]))
		fn.write(ingredient_info)

ingredient_to_check=yaml.load(open(ingredient_file))
check_to_ingredient={}
for ingredient in ingredient_to_check:
	if ingredient_to_check[ingredient] and ingredient in ingredient_to_ip:
		for check in ingredient_to_check[ingredient]:
			if check not in check_to_ingredient:
				check_to_ingredient[check]=set()
			check_to_ingredient[check].add(ingredient)

check_to_command=yaml.load(open(check_file))
with open(active_file,'a') as fn:
	for check in check_to_ingredient:
		service_info="define service {\n\tuse\t%s\n\thostgroup_name\t%s\n\tservice_description\t%s\n\tcheck_command\t%s\n\t}\n"%(Service_Use,','.join([env+'_'+x for x in check_to_ingredient[check]]),check,check_to_command[check])
		fn.write(service_info)
		ips=[env+'_'+ip+','+check for x in check_to_ingredient[check] for ip in ingredient_to_ip[x]]
		ips={}.fromkeys(ips).keys()
		servicegroup_info="define servicegroup {\n\tservicegroup_name\t%s\n\talias\t%s\n\tmembers\t%s\n\t}\n"%(env+'_'+check,env+'_'+check,','.join(ips))
		fn.write(servicegroup_info)

#write passive_file:passive_env.cfg

with open(passive_file,'w') as fn:
	for ip in ip_to_ingredient:
		use=Windows_Host_Passive_Use if ip in windows_hosts['windows'] else Linux_Host_Passive_Use
		host_info="define host {\n\tuse\t%s\n\thost_name\t%s\n\talias\t%s\n\taddress\t%s\n\t}\n"%(use,env+'_'+ip,env+'_'+ip,ip)
		fn.write(host_info)
	for ingredient in ingredient_to_ip:
		ingredient_info="define hostgroup {\n\thostgroup_name\t%s\n\talias\t%s\n\tmembers\t%s\n\t}\n"%(env+'_'+ingredient,env+'_'+ingredient,','.join([env+'_'+ip for ip in ingredient_to_ip[ingredient]]))
		fn.write(ingredient_info)

with open(passive_file,'a') as fn:
	for check in check_to_ingredient:
		# service_info="define service {\n\tuse\t%s\n\thostgroup_name\t%s\n\tservice_description\t%s\n\tcheck_command\t%s\n\t}\n"%(Passive_Service_Use,','.join([env+'_'+x for x in check_to_ingredient[check]]),check,check_to_command[check][0])
		service_info="define service {\n\tuse\t%s\n\thostgroup_name\t%s\n\tservice_description\t%s\n\tcheck_command\t%s\n\t}\n"%(Passive_Service_Use,','.join([env+'_'+x for x in check_to_ingredient[check]]),check,"check_dummy!2")
		fn.write(service_info)
		ips=[env+'_'+ip+','+check for x in check_to_ingredient[check] for ip in ingredient_to_ip[x]]
		ips={}.fromkeys(ips).keys()
		servicegroup_info="define servicegroup {\n\tservicegroup_name\t%s\n\talias\t%s\n\tmembers\t%s\n\t}\n"%(env+'_'+check,env+'_'+check,','.join(ips))
		fn.write(servicegroup_info)
