import ConfigParser

config = ConfigParser.RawConfigParser()

# When adding sections or items, add them in the reverse order of
# how you want them to be displayed in the actual file.
# In addition, please note that using RawConfigParser's and the raw
# mode of ConfigParser's respective set functions, you can assign
# non-string values to keys internally, but will receive an error
# when attempting to write to a file or when you get it in non-raw
# mode. SafeConfigParser does not allow such assignments to take place.

config_section='config1'


server = 'ldap://directory.cwds.io'
src_dn = "ou=Group,dc=cwds,dc=io"
dst_dn = "cn=logs-dev-test,ou=Group,dc=cwds,dc=io"


bind_dn="cn=ldap search,ou=People,dc=cwds,dc=io"
pw = "uQ8w39CWEp$UF#%7"

filter = '(&(objectClass=groupOfNames)(|(ou=developers)(cn=logs-dev)))'



config.add_section(config_section)
config.set(config_section, 'verbose', False)
config.set(config_section, 'server', server)
config.set(config_section, 'base_dn', src_dn)
config.set(config_section, 'dst_dn', dst_dn)
config.set(config_section, 'bind_dn', bind_dn)
config.set(config_section, 'bind_pwd', pw)
config.set(config_section, 'filter', filter)
config.set(config_section, 'attrs', "['member']")


# Writing our configuration file to 'example.cfg'
with open('example.cfg', 'wb') as configfile:
    config.write(configfile)
