#!/usr/bin/env python

from elasticsearch import Elasticsearch
from optparse import OptionParser
import ConfigParser

options=[]
config_section=""

usage = "usage: %prog [options] filter [attrs]"
parser = OptionParser(usage)
parser.add_option("-f", "--file", dest="filename", help="read configuration from FILENAME")
parser.add_option("-c", "--config", dest="config_section", help="configuration section in FILENAME")
parser.add_option("-v", "--verbose", help="enable verbose mode", action="store_true", dest="verbose")
parser.add_option("-q", "--quiet", help="enable quiet mode", action="store_false", dest="verbose")

(options, args) = parser.parse_args()
if (options.filename):
    if not(options.config_section):
        parser.error("Options -f <filename> have to use with -c config_section")
        sys.exit()

    config = ConfigParser.ConfigParser()
    config.read(options.filename)
    options.verbose         = config.get(options.config_section, 'verbose', 0)
    options.ESHost           = config.get(options.config_section, 'elasticsearchHosts', 0)
    options.ESPort           = config.get(options.config_section, 'elasticsearchPort', 0)
    options.ESUser          = config.get(options.config_section, 'elasticsearchXpackUser', 0)
    options.ESPass          = config.get(options.config_section, 'elasticsearchXpackPassword', 0)
    options.ESAliasPrefix   = config.get(options.config_section, 'elasticsearchAliasPrefix', 0)
    options.ESIndexPrefixL  = config.get(options.config_section, 'elasticsearchIndexPrefixList', 0)
    options.ESCluster       = config.get(options.config_section, 'elasticsearchCluster', 0)
    options.ESScheme        = config.get(options.config_section, 'elasticsearchScheme', 0)
    options.ESIndexKeep     = config.get(options.config_section, 'elasticsearchIndexkeep', 0)

else:
    parser.error("incorrect number of arguments")
if (options.verbose == True ):
    print("reading %s..." % options.filename)

try:
    # for now we use HTTP context for ES
    es = Elasticsearch(
        options.ESHost,
        http_auth=(options.ESUser, options.ESPass),
        scheme=options.ESScheme,
        port=options.ESPort,
    )
    print "Connected", es.info()
except Exception as ex:
    print "Error:", ex
    exit(1)

removelist =[]

for myindex in set(options.ESIndexPrefixL.split(',')):
    ESIndices=sorted(es.indices.get(myindex))
    ESAlias=sorted(es.indices.get_alias(name=options.ESAliasPrefix))
    toremove=sorted(set(ESIndices)-set(ESAlias))
    for i in range(1,int(options.ESIndexKeep)):
        if len(toremove)>0:
            toremove.pop()
    removelist+=toremove

for index in removelist:
    resultes = es.indices.delete(index=index)
    print ("Removing index {} status: {}".format(index,resultes))
