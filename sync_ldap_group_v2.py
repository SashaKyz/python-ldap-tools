#!/usr/bin/env python

import ldap
import sys
import ldap.modlist as modlist
import datetime
from optparse import OptionParser
import ConfigParser


options=[]
args=[]
attrs=[]
config_section=""


usage = "usage: %prog [options] filter [attrs]"
parser = OptionParser(usage)
parser.add_option("-f", "--file", dest="filename", help="read configuration from FILENAME")
parser.add_option("-c", "--config", dest="config_section", help="configuration section in FILENAME")

parser.add_option("-v", "--verbose", help="enable verbose mode", action="store_true", dest="verbose")
parser.add_option("-q", "--quiet", help="enable quiet mode", action="store_false", dest="verbose")

parser.add_option("-s", "--server",default="ldap://directory.cwds.io", dest="server", help="LDAP server name")
parser.add_option("-b", "--base_dn", default="ou=Group,dc=cwds,dc=io", dest="src_dn", help="LDAP base_dn")
parser.add_option("-d", "--dst_dn", dest="dst_dn", help="LDAP dst_dn group name")
parser.add_option("-u", "--bind_dn", default="", dest="bind_dn", help="LDAP bind_dn name")
parser.add_option("-p", "--bind_pwd", default="", dest="bind_pwd", help="LDAP bind password")



(options, args) = parser.parse_args()
if (len(args) > 0): 
       options.filter = args[0]
       if (len(args) > 1):
          options.attrs = args[1]
          if (len(args) > 2):
            parser.error("incorrect number of arguments")    
       else:
          options.attrs = ['member']
elif (options.filename):
        if not(options.config_section):
            parser.error("Options -f <filename> have to use with -c config_section")
            sys.exit()
          
        config = ConfigParser.ConfigParser()
        config.read(options.filename)
        options.verbose     = config.get(options.config_section, 'verbose', 0)
        options.server      = config.get(options.config_section, 'server', 0)
        options.src_dn      = config.get(options.config_section, 'base_dn', 0)
        options.dst_dn      = config.get(options.config_section, 'dst_dn', 0)
        options.bind_dn     = config.get(options.config_section, 'bind_dn', 0)
        options.bind_pwd    = config.get(options.config_section, 'bind_pwd', 0)
        options.filter      = config.get(options.config_section, 'filter', 0)
        options.attrs = ['member']
else:
            parser.error("incorrect number of arguments")    

if not (options.dst_dn): 
            parser.error("options -d must set")    

if (options.verbose == True ):
        print("reading %s..." % options.filename)

ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
l = ldap.initialize(options.server)
try:
    l.simple_bind_s(options.bind_dn,options.bind_pwd)
except ldap.LDAPError, e:
    print e.message['info']
    if type(e.message) == dict and e.message.has_key('desc'):
        print e.message['desc']
    else:
        print e
    sys.exit()

scan_dyn_group_res = l.search_s(options.src_dn,ldap.SCOPE_SUBTREE, options.filter, options.attrs)
attrs = {}
attrs['objectclass'] = ['top','groupofnames']
member_list = set()
for dyn_group_res in scan_dyn_group_res:
   member_list.update(dyn_group_res[1]['member'])

attrs['member'] = list(member_list)
attrs['description'] = ['Autoedited group from python script {:%Y-%m-%d %H:%M:%S} '.format(datetime.datetime.now())]

try:
  scan_old_group_search = l.search_s(options.dst_dn,ldap.SCOPE_SUBTREE, '(objectClass=*)', ['objectclass','member','description'])
  ldif = modlist.modifyModlist(scan_old_group_search[0][1],attrs)
  l.modify_s(options.dst_dn,ldif)

except ldap.LDAPError, e:
    if type(e.message) == dict and e.message.has_key('desc') and (e.message['desc']=='No such object') :
        print "Can't update group %s Error: %. Try to create new. " % options.dst_dn, e.message['desc']
        ldif = modlist.addModlist(attrs)
        l.add_s(options.dst_dn,ldif)
        sys.exit()
        
    print e


l.unbind()

