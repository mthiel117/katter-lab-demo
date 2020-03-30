#!/usr/bin/python

import requests
import json
import os
import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning

CVP_HOST = "192.168.51.196"
CVP_USER = "cvpadmin"
CVP_PWD = "N3tsupp0rt"

CONFIGLET_SUBDIR = 'configlets'   # subdirectory containing configlet text files

# To remove warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Login to CVP
auth_data = json.dumps({"userId": CVP_USER, "password": CVP_PWD})
auth_url = "https://%s/cvpservice/login/authenticate.do" % CVP_HOST
auth_response = requests.post(auth_url, data=auth_data, verify=False)
assert auth_response.ok
cookies = auth_response.cookies


def search_configlets(query, start=0, end=0):
        configlet_search_url = ('https://%s/cvpservice/configlet/searchConfiglets.do?queryparam=%s&startIndex=%d&endIndex=%d' %(CVP_HOST, query, start, end))
        configlet_search_response = requests.get(configlet_search_url, data=None, cookies=cookies, verify=False)
        configlet_list_json = configlet_search_response.json()
        #pprint.pprint(configlet_list_json)

        #print(configlet_list_json['total'])
        if configlet_list_json['total'] > 0:
                #print("Configlets with similar names exist:\n")
                #for configlet in configlet_list_json['data']:
                #        print(configlet['name'])
                return True
        else:
                return False

def create_new_configlet(configlet_name, filename):
    with open(CONFIGLET_SUBDIR + "/" +filename, "r") as fopen:  # open file in sibdirectory
        configlet_content = fopen.read() # read in the file contents to create configlet
        # Create new Configlet using the file content
        newConfiglet_data = json.dumps({"config": configlet_content, "name": configlet_name})
        newConfiglet_url = "https://%s/cvpservice/configlet/addConfiglet.do" % CVP_HOST
        newConfiglet_response = requests.post(newConfiglet_url, data=newConfiglet_data, cookies=cookies, verify=False)
        #print(newConfiglet_response.json())  # check for any errors

    return

def update_existing_configlet(configlet_name, filename):
    #call getConfigletByName.do to key keyname value to pass to updateConfiglet.do
    configletbyname_search_url = ('https://%s/cvpservice/configlet/getConfigletByName.do?name=%s' %(CVP_HOST, configlet_name))
    configletbyname_search_response = requests.get(configletbyname_search_url, data=None, cookies=cookies, verify=False)
    configletbyname_json = configletbyname_search_response.json()
    configlet_key = configletbyname_json['key']

    with open(CONFIGLET_SUBDIR + "/" +filename, "r") as fopen:  # open file in sibdirectory
        configlet_content = fopen.read() # read in the file contents to create configlet
        # Create new Configlet using the file content
        newConfiglet_data = json.dumps({"config": configlet_content, "name": configlet_name, "key": configlet_key, "waitForTaskIds": False, "reconciled": False})
        newConfiglet_url = "https://%s/cvpservice/configlet/updateConfiglet.do" % CVP_HOST
        newConfiglet_response = requests.post(newConfiglet_url, data=newConfiglet_data, cookies=cookies, verify=False)
        #print(newConfiglet_response.json())  # check for any errors
       
    return


def createconfiglets():

    # Reading config from a file
    # r=root, d=directories, f=files
    for r,d,f in os.walk(CONFIGLET_SUBDIR):
        for filename in f:
            if '.txt' in filename:  # this is a configlet file 
    
                configlet_name = ''.join(filename.split())[:-4].upper()

                configlet_name_exists = search_configlets(configlet_name)
                if configlet_name_exists:
                    update_existing_configlet(configlet_name, filename)
                    print("updating existing configlet: " + configlet_name)
                    #  still need to create logic for this
                else:
                    create_new_configlet(configlet_name, filename)
                    print("creating new configlet: " + configlet_name)

def main():
        createconfiglets()
        
if __name__ == "__main__":
    main()
