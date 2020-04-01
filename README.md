# Demo Playbooks & Python Scripts

## Python Examples

### 1. Using eAPI - return values from Spine switch

```
./spine1-info.py
```

### 2. Using eAPI - return values from multiple switches

```
./net-info.py
```

### 3. Push Configlets from ./configlets to CVP

```
./pushconfigs_to_cvp.py
```

## Ansible Examples

### 4. Create Configlets from CSV

|  |  |
|--|--|
| Input CSV | ./datafiles/switch_info.csv |
| Output Configlets | ./configlets/. |

```
ansible-playbook create-configlets.yml
```