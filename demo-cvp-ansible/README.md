# Demo Playbooks

### 1. Backup running-config on each device to ./config_backup

```
ansible-playbook backup-configs.yml
```

### 2. Upload configlets to CVP from directory ./configlets

```
ansible-playbook configlet-uploader.yml
```

### 3. Bind Configlets to single device dc1-poe-leaf-sw1
Makes use of Tags to provision or rollback changes to the device.  Static list of configlets are defined in the playbook.

```
ansible-playbook device-configlets.yml --tags provision

ansible-playbook device-configlets.yml --tags rollback

```