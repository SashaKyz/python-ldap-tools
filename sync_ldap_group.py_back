#!/usr/bin/env python

import ldap
import sys
import ldap.modlist as modlist
import datetime
from pprint import pprint

server = 'ldap://directory.cwds.io'
src_dn = "ou=Group,dc=cwds,dc=io"
dst_dn = "cn=logs-dev-test,ou=Group,dc=cwds,dc=io"


bind_dn="cn=ldap search,ou=People,dc=cwds,dc=io"
pw = "uQ8w39CWEp$UF#%7"

filter = '(&(objectClass=groupOfNames)(|(ou=developers)(cn=logs-dev)))'
attrs = ['member']




l = ldap.initialize(server)
try:
    l.simple_bind_s(bind_dn,pw)
except ldap.LDAPError, e:
    print e.message['info']
    if type(e.message) == dict and e.message.has_key('desc'):
        print e.message['desc']
    else:
        print e
    sys.exit()

scan_dyn_group_res = l.search_s(src_dn,ldap.SCOPE_SUBTREE, filter, attrs)


print "scan_dyn_group_res:"
pprint(scan_dyn_group_res)
print "-"*32



attrs = {}
attrs['objectclass'] = ['top','groupofnames']
member_list = set()
for dyn_group_res in scan_dyn_group_res:
   member_list.update(dyn_group_res[1]['member'])

attrs['member'] = list(member_list)

#  attrs['member'] = scan_dyn_group_res[0][dyn_group_res]['member']
attrs['description'] = 'Autoedited group from python '+str(datetime.datetime.now())

print "Attrs:"
pprint(attrs)
print "-"*32


try:
  scan_old_group_search = l.search_s(dst_dn,ldap.SCOPE_SUBTREE, '(objectClass=*)', ['objectclass','member','description'])
  print "scan_old_group_res:"
  pprint(scan_old_group_search)
  print "-"*32
  ldif = modlist.modifyModlist(scan_old_group_search[0][1],attrs)
  l.modify_s(dst_dn,ldif)

except ldap.LDAPError, e:
    if type(e.message) == dict and e.message.has_key('desc') and (e.message['desc']=='No such object') :
        print "Test !!!!!!! "+e.message['desc']
        ldif = modlist.addModlist(attrs)
        l.add_s(dst_dn,ldif)
        sys.exit()
        
    print e


l.unbind()