# Home Server ansible

This repository configures my home server Ubuntu server.

Two core playbooks exist:

## initial_config.yml
This should run after creating initial user and password, to allow ansible user to execute the second playbook.

Since ansible.cfg defines a different inventory file, inventory must be passed explicitly.

Example usage:
```bash
ansible-playbook initial_config.yml -i inventories/inventory_newhost.ini --ask-become-pass --ask-pass
```

## configure.yaml
This configures the server minimally to allow installing some docker images using portainer.
It will perform the following:
1. Create service accounts for docker apps
2. Create local users and groups
3. Ensure ZFS pool exists and underlying structure exists
4. Add UFW rules for basic access (warning, with bad configuration this could block your own access)

With ansible.cfg config, no need to explicitly pass inventory or vault pass. You'll need your own `.vault_pwd_file` for this to work, and to create your own encrypted strings.

Example usage:
```bash
ansible-playbook ansible-playbook configure.yaml
```
