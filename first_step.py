#!/usr/bin/env python

import ldap
import sys
import ldap.modlist as modlist
import datetime
from pprint import pprint

server = 'ldap://directory.cwds.io'
src_dn = "cn=logs-dev-env,ou=Group,dc=cwds,dc=io"
dst_dn = "cn=logs-dev-test,ou=Group,dc=cwds,dc=io"


bind_dn="cn=ldap search,ou=People,dc=cwds,dc=io"
pw = "uQ8w39CWEp$UF#%7"

filter = '(objectclass=*)'
attrs = ['member']





l = ldap.initialize(server)
try:
#    l.start_tls_s()
    l.simple_bind_s(bind_dn,pw)
except ldap.LDAPError, e:
    print e.message['info']
    if type(e.message) == dict and e.message.has_key('desc'):
        print e.message['desc']
    else:
        print e
    sys.exit()

scan_dyn_group_res = l.search_s(src_dn,ldap.SCOPE_SUBTREE, filter, attrs)
scan_old_group_res = l.search_s(dst_dn,ldap.SCOPE_SUBTREE, filter, ['*'])[0][1]
attrs = {}
attrs['objectclass'] = ['top','groupofnames']
attrs['cn'] = ['logs-dev-test']
attrs['member'] = scan_dyn_group_res[0][1]['member']
attrs['description'] = 'Autoedited group from python '+str(datetime.datetime.now())

print "Attrs:"
pprint(attrs)
print "-"*32

print "scan_dyn_group_res:"
pprint(scan_dyn_group_res)
print "-"*32

print "scan_old_group_res:"
pprint(scan_old_group_res)
print "-"*32



ldif = modlist.modifyModlist(scan_old_group_res,attrs)
#l.add_s(dst_dn,new_ldif)
l.modify_s(dst_dn,ldif)

l.unbind()