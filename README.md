Gaucho
===========================================

Gaucho is simply some Python scripts to access the 
[Rancher](https://github.com/rancher/rancher)'s API to perform tasks which
I need to have executed through my deployment workflow.

At this point, it does not contain much but it might grow as I get more 
requirements.

Contributions are welcome if you want to use it and add to it.

## Usage
```
./services.py --help
Usage: ./services.py COMMAND <options>

Available commands:
 query    Retrieves the service information.
 upgrade  Upgrades a service

Use './services.py <command> --help' for individual command help.
```

## Rancher API Access

If you run Gaucho in a container on Rancher, rather than set the environment 
variables manually for the Rancher URL, access key, etc, use the following 
labels to have Rancher automatically do it for you.

```
io.rancher.container.create_agent=true
io.rancher.container.agent.role=environment
```

See [Service Accounts in Rancher](http://docs.rancher.com/rancher/latest/en/rancher-services/service-accounts/)
for more information on this feature.

## Dependencies

 - requests
 - baker

