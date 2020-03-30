#!/usr/bin/python
#
# Example eAPI script to pull info from spine1
#
from jsonrpclib import Server
import ssl

# Ignore SSL connection warnings
try:
  _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
  pass
else:
  ssl._create_default_https_context = _create_unverified_https_context

# Vars
userid = "admin"
password = "N3tsupp0rt"
switchaddr = "192.168.51.75" # Switch Mgmt Address
RESTURL = "https://" + userid + ":" + password + "@" + switchaddr + "/command-api"

# Instantiate switch object
switch = Server(RESTURL)

# run command(s) against switch object
# list of command output returned in a List (array) or JSON key:value pairs
response = switch.runCmds(1, ["show hostname",
                              "show version",
                              "show ip interface Management1"])

hostname = response[0]["hostname"]
mgmtip = response[2]["interfaces"]["Management1"]["interfaceAddress"]["primaryIp"]["address"]

# Gather data and print out useful info

print "\n"
print "Information for " + hostname + " - " + mgmtip
print "-------------------------------------------------------"
print "System MAC....: ", response[1]["systemMacAddress"]
print "Model.........: ", response[1]["modelName"]
print "Total Memory..: ", response[1]["memTotal"]
print "Free Memory...: ", response[1]["memFree"]
print "EOS Version...: ", response[1]["version"]
print "Uptime(secs)..: ", response[1]["uptime"]
print "\n"
