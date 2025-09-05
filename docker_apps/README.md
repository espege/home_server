# Docker Apps

This folder contains docker apps to be used with role `docker_compose_generator`

## Docker app sample structure for app `grafana`

``` bash
├── docker-compose.yaml.j2 # mandatory
├── grafana # if folder matches app name, this child structure will be copied to docker host
│   └── config.alloy.j2
└── grafana-vars.yaml # optional
```

# {docker-app-name}-vars.yaml

The role `docker_compose_generator` will leverage the -vars file to control some resource creation. Here is an overview of keys and outcomes.

Expected keys:

| Key                 | Type  | Example        | Expected Value    | Outcome |
|---------------------|-------|----------------|-------------------|---------|
| state               | string| present        | [present, absent] | create/delete configs |
| connect_to_traefik  | bool  | true           | [True, False] | connect external networks to traefik |
| local_compose_output| bool  | true           | [True, False] | output docker_compose file on ansible controller instead of remote host |
| linux_users         | map   | {name: plex}   | map with keys: name,comment,shell | create specific users |
| linux_extra_groups      | list  |  ["media"]  | Standalone Groups | Create linux groups |
| bind_vol_owner      | string   | plex   | valid user name | override root as default owner for `dict` bind volumes |
| bind_vol_group_is_extra | bool | true | [True, False]  | override root as default group for `dict` bind volumes |
| ufw      | list(map)   |  {rule: allow, proto: tcp[...]}  | `ufw_config` role inputs | Manage app-specific UFW rules |
| backup_volumes      | list(string)   |  ["path/to/volume"]  | Specific Docker Volume paths | Adds a cron job to backup these volumes |

### xyz-vars.yaml variables and outcomes for `local_compose_output` and `connect_to_traefik`

```mermaid
flowchart TD
    %% Define Logic Elements
    Start((Start))
    End((End))
    CR[state: present]
    RM[state: absent]
    local_compose_output{local_compose_output defined}
    TraefikTrue[Add External Network to Traefik]
    TraefikConnect{Connect To Traefik}
    Traefik_Ext_Net{External Network defined in docker-compose}
    local_out[Output docker_compose files to default localhost location]
    remote_out[Output docker_compose to default docker_compose_generator_default_bind_path]


    %% Chart relationships
    Start --> state
    state{state}
    state -->|present| CR
    CR --> TraefikConnect
    state -->|absent| RM
    TraefikConnect -->|true| Traefik_Ext_Net
    TraefikConnect -->|false| local_compose_output
    Traefik_Ext_Net -->|true| TraefikTrue
    Traefik_Ext_Net -->|false| local_compose_output
    TraefikTrue --> local_compose_output
    local_compose_output{local_compose_output}
    local_compose_output -->|true| local_out
    local_compose_output -->|false| remote_out
    local_out --> End
    remote_out --> End
```


### xyz-vars.yaml variables and outcomes for `linux_users`
```mermaid
---
config:
  theme: 'forest'
---

flowchart TD
    %% Define Logic Elements
    Start((Start))
    End((End))
    User{linux_users defined}
    create[Create user]
    bindvol{bind_vol_owner defined}
    extra_groups{linux_extra_groups defined}
    create_extra[create groups]
    bind_vol_extra{bind_vol_group_is_extra defined}
    bind_vol_action[chmod group to FIRST bind_vol_extra]
    chmod[chown docker-compose volumes]

    %% Chart relationships
    Start --> User
    User -->|true| create
    User -->|false| bindvol
    create --> bindvol
    bindvol -->|true| chmod
    chmod --> bind_vol_extra
    bindvol -->|false| End
    Start --> extra_groups
    extra_groups -->|true| create_extra
    create_extra -->bind_vol_extra
    extra_groups -->|false| End
    bind_vol_extra -->|true| bind_vol_action
    bind_vol_action --> End
    bind_vol_extra -->|false| End


    %% Style for lozanges (decision nodes)
    classDef lozenge fill:#f6a,stroke:#333,stroke-width:2px;
    class User,extra_groups,bind_vol_extra,bindvol lozenge;
```

### xyz-vars.yaml variables and outcomes for `ufw`
```mermaid
---
config:
  theme: 'forest'
---

flowchart TD
    %% Define Logic Elements
    Start((Start))
    End((End))
    ufw{ufw is defined}
    role[Call Role ufw_config]

    %% Chart relationships
    Start --> ufw
    ufw -->|defined| role
    ufw -->|undefined|End
    role --> End

    %% Style for lozanges (decision nodes)
    classDef lozenge fill:#f6a,stroke:#333,stroke-width:2px;
    class ufw lozenge;
```
