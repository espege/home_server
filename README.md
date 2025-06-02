# Home Server ansible

This repository configures my home server Ubuntu server.

Two core playbooks exist:

## initial_config.yml
This should run after creating initial user and password, to allow ansible user to execute the second playbook.

## configure.yaml
This configures the server minimally to allow installing some docker images using portainer.
It will perform the following:
1. Create service accounts for docker apps
2. Create local users and groups
3. Ensure ZFS pool exists and underlying structure exists
4. Add UFW rules for basic access (warning, with bad configuration this could block your own access)
