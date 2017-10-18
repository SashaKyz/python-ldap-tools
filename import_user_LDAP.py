#!/usr/bin/env python

import ldap
import sys
import ldap.modlist as modlist
import datetime
from optparse import OptionParser
from xlrd import open_workbook
import ConfigParser
import unicodedata
from passlib.hash import ldap_md5_crypt
import string
import random

def pw_gen(size = 12, chars=string.ascii_letters + string.digits ):
    return ''.join(random.choice(chars) for _ in range(random.randint(8,size)))

wb = open_workbook('/TMP/Users_list.xlsx')
values = []
for s in wb.sheets():
    print 'Sheet:',s.name
    for row in range(1, s.nrows):
        col_names = s.row(0)
        col_value = []
        for name, col in zip(col_names, range(s.ncols)):
            value  = (s.cell(row,col).value)
            try : value = str(int(value))
            except : pass
            col_value.append((name.value, value))
        values.append(col_value)
print values

print "-"*80


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
    options.passwdlen   = int(config.get(options.config_section, 'passwdlen', 0))
    options.attrs = ['']
else:
    parser.error("incorrect number of arguments")

if not (options.dst_dn):
    parser.error("options -d must set")

if (options.verbose == True ):
    print("reading %s..." % options.filename)

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

attrs1 = {}
attrs1['objectclass'] = ['top','groupofnames']
attrs1['member'] = ['cn=ldap search,ou=People,dc=cwds,dc=io']
attrs1['description'] = 'Autoedited group from python script '+str(datetime.datetime.now())
member_list = set()
try:
    scan_old_group_search = l.search_s(options.dst_dn,ldap.SCOPE_SUBTREE, '(objectClass=*)', ['objectclass','member','description'])

except ldap.LDAPError, e:
    if type(e.message) == dict and e.message.has_key('desc') and (e.message['desc']=='No such object') :
        ldif1 = modlist.addModlist(attrs1)
        l.add_s(options.dst_dn,ldif1)
        scan_old_group_search = l.search_s(options.dst_dn,ldap.SCOPE_SUBTREE, '(objectClass=*)', ['objectclass','member','description'])
    print e

for keys in values:
    filter = unicodedata.normalize('NFKD','(&(objectClass=inetOrgPerson)(|(uid='+keys[4][1]+')(&(sn='+keys[1][1]+')(givenName='+keys[0][1]+'))(mail='+keys[3][1]+')))').encode('ascii','ignore')
    scan_user_search = l.search_s(options.src_dn,ldap.SCOPE_SUBTREE, filter)
    if scan_user_search != []:
        print "Skipping user\tDN:", scan_user_search[0][0],"\t\tUID: ", keys[4][1]
        member_list.add(scan_user_search[0][0])
    else:
        attrs = {}
        attrs['objectclass'] = ['person','organizationalperson','inetorgperson','top']
        attrs['cn'] = unicodedata.normalize('NFKD',keys[0][1]+' '+keys[1][1]).encode('ascii','ignore')
        attrs['sn'] = unicodedata.normalize('NFKD',keys[1][1]).encode('ascii','ignore')
        attrs['uid'] = unicodedata.normalize('NFKD',keys[4][1]).encode('ascii','ignore')
        attrs['givenName'] = unicodedata.normalize('NFKD',keys[0][1]).encode('ascii','ignore')
        attrs['mail'] = unicodedata.normalize('NFKD',keys[3][1]).encode('ascii','ignore')
        userpassword = pw_gen(options.passwdlen)
        attrs['userPassword'] = ldap_md5_crypt.hash(userpassword)
        attrs['description'] = 'User object created by python script'
        ldif = modlist.addModlist(attrs)
        dn = "cn="+attrs['cn']+","+options.src_dn
        print "Creating user\tDN:",dn,"\t\tUID: ",keys[4][1]
        l.add_s(dn,ldif)
        member_list.add(dn)



attrs1['member'] = list(member_list)
ldif1 = modlist.modifyModlist(scan_old_group_search[0][1],attrs1)
l.modify_s(options.dst_dn,ldif1)

l.unbind()

