#!/usr/bin/python

import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pprint

CVP_HOST = "192.168.1.249"
CVP_USER = "cvpadmin"
CVP_PWD = "cvpadmin123"

SUBNET_CONFIGLET_MAPPING = {'10.1.1':'DEVICE-10.1.1-MGMT',
                            '10.2.1':'DEVICE-10.2.1-MGMT'}

CONTAINER_MAPPING = {'10.1.1':'VSS',
                     '10.2.1':'BBW'}
                
TASKS_DESCRIPTIONS = []

# To remove warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Login into CVP
auth_data = json.dumps({"userId": CVP_USER, "password": CVP_PWD})
auth_url = "https://%s/cvpservice/login/authenticate.do" % CVP_HOST
auth_response = requests.post(auth_url, data=auth_data, verify=False)
assert auth_response.ok
cookies = auth_response.cookies

def get_configlet_key(switch_mgmt_configlet_name):
        configlet_url = ('https://%s/cvpservice/configlet/getConfigletByName.do?name=%s' %(CVP_HOST, switch_mgmt_configlet_name))
        configlet_response = requests.get(configlet_url, data=None, cookies=cookies, verify=False)
        configlet_list_json = configlet_response.json()
      
        #if configlet_list_json != []:
        if len(configlet_list_json) > 2:
                return(configlet_list_json['key'])
        else:
                print("Exiting...  Could not find assigned configlet and key.")
                print("Likely need to run createconfiglets script to create and upload configlets into CVP")
                exit()

def get_undefined_switches():
        device_search_url = ('https://%s/cvpservice/inventory/devices' %(CVP_HOST))
        device_search_response = requests.get(device_search_url, cookies=cookies, verify=False)
        device_list_json = device_search_response.json()
        undefined_switches = [] # list of switches we need to configure

        for device in device_list_json:
                if device['parentContainerKey'] == 'undefined_container':
                        undefined_switches.append(device)
        return undefined_switches

def get_target_container_key(target_container_name):
        url_path = ('https://%s/cvpservice/inventory/containers?name=%s' %(CVP_HOST, target_container_name))
        response = requests.get(url_path, cookies=cookies, verify=False)
        container_json = response.json()
        if container_json == []:
            print('{0} container not found.'.format(target_container_name))
            quit()
        else:
            container_key = container_json[0]['Key']
            return(container_key)

def move_switch_to_container(switch,target_container_name,target_container_key):
    undefined_container = 'undefined_container'
    url_path = ('https://%s/cvpservice/provisioning/addTempAction.do?format=topology&queryParam=&nodeId=root' %(CVP_HOST))
    info = 'Move %s to container: %s' % (switch['hostname'], target_container_name)
    payload = {"data": [{
                        "info": info ,
                        "infoPreview": info,
                        "action": "update",
                        "nodeType": "netelement",
                        "nodeId": switch['systemMacAddress'],
                        "toId": target_container_key,
                        "fromId": undefined_container,
                        "nodeName": switch['fqdn'],
                        "toName": target_container_name,
                        "toIdType": "container",
                        "childTasks": [],
                        "parentTask": ""}]}


    response = requests.post(url_path, data=json.dumps(payload), cookies=cookies, verify=False)

    return(info)

def get_current_configlets(switch):
    url_path = ('https://%s/cvpservice/provisioning/getConfigletsByNetElementId.do?netElementId=%s&queryParam=&startIndex=0&endIndex=0' % (CVP_HOST, switch['systemMacAddress']))
    response = requests.get(url_path, cookies=cookies, verify=False)
    response_json = response.json()
    return(response_json['configletList'])

def apply_configlet_to_switch(switch,new_configlet_key,new_configlet_name,current_configlets):
    url_path = ('https://%s/cvpservice/provisioning/addTempAction.do?format=topology&queryParam=&nodeId=root' % (CVP_HOST))
    
    ################API Data################
    # Build Configlet List from Current & New Management Configlets
    configlet_list = []
    configlet_key_list = []
    for configlet in current_configlets:
        configlet_list.append(configlet['name'])
        configlet_key_list.append(configlet['key'])
    configlet_list.append(new_configlet_name)
    configlet_key_list.append(new_configlet_key)

    #Information
    info = 'Assign Configlet {0}: to Device {1}'.format(new_configlet_name, switch['hostname'])
    payload = json.dumps({'data': [{'info': info,
                    'infoPreview': info,
                    'note': '',
                    'action': 'associate',
                    'nodeType': 'configlet',
                    'nodeId': '',
                    'configletList': configlet_key_list,
                    'configletNamesList': configlet_list,
                    'ignoreConfigletNamesList': [],
                    'ignoreConfigletList': [],
                    'configletBuilderList': [],
                    'configletBuilderNamesList': [],
                    'ignoreConfigletBuilderList': [],
                    'ignoreConfigletBuilderNamesList': [],
                    'toId': switch['systemMacAddress'],
                    'toIdType': 'netelement',
                    'fromId': '',
                    'nodeName': '',
                    'fromName': '',
                    'toName': switch['fqdn'],
                    'nodeIpAddress': switch['ipAddress'],
                    'nodeTargetIpAddress': switch['ipAddress'],
                    'childTasks': [],
                    'parentTask': ''}]})

    response = requests.post(url_path, data=payload, cookies=cookies, verify=False)




def save_topology():
  url_path = ('https://%s/cvpservice/provisioning/saveTopology.do' % (CVP_HOST))
  data = '[]'
  response = requests.post(url_path, data=data, cookies=cookies, verify=False)

def get_tasks():
        tasklist = []
        url_path = ('https://%s/cvpservice/task/getTasks.do?startIndex=0&endIndex=50' % (CVP_HOST))
        response = requests.get(url_path, cookies=cookies, verify=False)
        response_json = response.json()
        tasks = response_json
        for task in tasks['data']:
            if task['currentTaskName'] == 'Submit':
                tasklist.append(task)
        return tasklist

def execute_tasks(all_tasks,target_task_descriptions):
    tasks_to_execute = []
    url_path = ('https://%s/cvpservice//task/executeTask.do' % (CVP_HOST))

    #Iterate through tasks to look for descriptions (created by 'info' variable in 'move_device_to_container' function)
    #If description is in the list, add task to a list of tasks to execute

    for task in all_tasks:
        if task['description'] in target_task_descriptions:
            tasks_to_execute.append(str(task['workOrderId']))
    payload = {"data": tasks_to_execute}
    response = requests.post(url_path, data=json.dumps(payload), cookies=cookies, verify=False)

def configure_switches(switchlist):
        for switch in switchlist:
                # Define Container & Configlet names for undefined switch
                switch_subnet = switch['ipAddress'].split('.')
                switch_subnet = ".".join(switch_subnet[:-1]) # remove 4th octet to get subnet
                target_container_name = CONTAINER_MAPPING[switch_subnet]
                

                # New management configlet to add to the device
                switch_mgmt_configlet_name = SUBNET_CONFIGLET_MAPPING[switch_subnet]
                switch_mgmt_configlet_key = get_configlet_key(switch_mgmt_configlet_name)

                print("Moving device: " + switch['hostname'] + " to container " + target_container_name + " and assigning configlet " + switch_mgmt_configlet_name) 

                target_container_key = get_target_container_key(target_container_name)
                             
                task_info = move_switch_to_container(switch,target_container_name,target_container_key)
                
                TASKS_DESCRIPTIONS.append(task_info)

                current_configlets = get_current_configlets(switch)
                
                apply_configlet_to_switch(switch,switch_mgmt_configlet_key,switch_mgmt_configlet_name,current_configlets)
                

def main():
      
        #Find switches sitting in the undefined container
        switches_to_configure = get_undefined_switches()

        # Move switches in the undefined container to new container and assign all configlets
        if (len(switches_to_configure)) > 0:
                print("Moving switches to final container and assigning configlets")
                configure_switches(switches_to_configure)

                # Save the topology after move and configlets are applied
                print("Saving Topology changes")
                save_topology()

                # Get a list of unsubitted tasks
                print("Executing Tasks")
                tasks_to_submit = get_tasks()
                # Execute all tasks generated by this script
                # TASK_DESCRIPTIONS has a list of tasks created buy this script
                execute_tasks(tasks_to_submit,TASKS_DESCRIPTIONS)
                print("Tasks execution complete.\nDevices are rebooting.  Standby for 5 minutes.")
        else:
                print("No devices found to provision.  Exiting.")
                exit()

if __name__ == "__main__":
    main()

