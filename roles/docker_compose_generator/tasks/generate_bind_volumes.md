# Playbook logic

## Always:

### Create bind volumes defined in "long" format
Create the bind volumes as defined in the docker-compose file if they use the key "source" in the volumes section.
Example:

```bash
volumes:
  - type: bind
    source: path/media
    target: /home/docker_app/media
```

#### Bind volume owner and group
**Important**: The long-form volumes will have their owners changed to *bind_vol_owner* if variable is defined in `xyz-vars.yaml`.
It will inherit a the first group from *linux_extra_groups* if *bind_vol_group_is_extra* is true

## Optional:
It checks if a directory structure exists for the docker_app, and if so, it copies
the entire structure to the remote directory.

Example:
```bash
automatic_ripping_machine
├── automatic_ripping_machine --> If folder exists with exact name as docker_app, then copy the entire folder structure
│   ├── config
│   │   └── arm.yaml
│   ├── home
│   └── logs
├── automatic_ripping_machine-vars.yaml
└── docker-compose.yaml.j2
```
