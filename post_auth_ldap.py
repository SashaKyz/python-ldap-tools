import re
import ldap

from pyovpn.plugin import *

#re_group = re.compile(r"^CN=([^,]+)")

# alternative for some LDAP servers:
re_group = re.compile(r"^cn=([^,]+)")

def ldap_groups_parse(res):
    ret = set()
    for g in res[0][1]['memberOf']:
        m = re.match(re_group, g)
        if m:
            ret.add(m.groups()[0])
    return ret

# this function is called by the Access Server after normal authentication
def post_auth(authcred, attributes, authret, info):
    print ("********** POST_AUTH", authcred, attributes, authret, info)

    # user properties to save
    proplist_save = {}

    group = "default"
    proplist = authret.setdefault('proplist', {})
    if info.get('auth_method') == 'ldap': # this code only operates when the Access Server auth method is set to LDAP
        # get the user's distinguished name
        user_dn = info['user_dn']

        # use our given LDAP context to perform queries
        with info['ldap_context'] as l:
            # get the LDAP group settings for this user
            ldap_groups = ldap_groups_parse(l.search_ext_s(user_dn, ldap.SCOPE_SUBTREE, attrlist=["memberOf"]))
            print ("********** LDAP_GROUPS", ldap_groups)


            # determine the access server group based on LDAP group settings; define as many as you need.
            if 'DevOps' in ldap_groups:
                group = "DevOps"
            elif 'testers-qa' in ldap_groups:
                group = "QA"
            elif 'dev-jenkins-users' in ldap_groups:
                group = "Developer"
            elif 'dev-jenkins-teamleads' in ldap_groups:
                group = "Developer"
            elif 'Implementation Team' in ldap_groups:
                group = "ImplementationTeam"

    print ("***** POST_AUTH: User group mapping found for", info['user_dn'], ", setting OpenVPN connection group to ", group, "...")
    authret['proplist']['conn_group'] = group
    proplist_save['conn_group'] = group

    return authret, proplist_save


