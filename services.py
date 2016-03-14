#!/usr/bin/env python
import baker
import json
import requests
import sys

HOST = "http://rancher.local:8080"
URL_SERVICE = "/v1/services/"
USERNAME = "userid"
PASSWORD = "password"

def get(url):
   r = requests.get(url, auth=(USERNAME, PASSWORD))
   r.raise_for_status()
   return r

def post(url, data):
   r = requests.post(url, data=json.dumps(data), auth=(USERNAME, PASSWORD))
   r.raise_for_status()

def print_json(data):
   print json.dumps(data, sort_keys=True, indent=3, separators=(',', ': '))


#
# Query the service configuration.
#
@baker.command(default=True, params={"service_id": "The ID of the service to read (optional)"})
def query(service_id=""):
   """Retrieves the service information.

   If you don't specify an ID, data for all services
   will be retrieved.
   """

   r = get(HOST + URL_SERVICE + service_id)
   print_json(r.json())


#
# Upgrades the service.
#
@baker.command(params={"service_id": "The ID of the service to upgrade.", "start_first": "Whether or not to start the new instance first before stopping the old one."})
def upgrade(service_id, start_first=True,
            batch_size=1, interval_millis=10000):
   """Upgrades a service

   Performs a service upgrade, keeping the same configuration, but otherwise 
   pulling new image as needed and starting new containers, dropping the old 
   ones.
   """

   upgrade_strategy = json.loads('{"inServiceStrategy": {"batchSize": 1,"intervalMillis": 10000,"startFirst": true,"launchConfig": {},"secondaryLaunchConfigs": []}}')
   upgrade_strategy['inServiceStrategy']['batchSize'] = batch_size
   upgrade_strategy['inServiceStrategy']['intervalMillis'] = interval_millis
   if start_first:
      upgrade_strategy['inServiceStrategy']['startFirst'] = "true"
   else:
      upgrade_strategy['inServiceStrategy']['startFirst'] = "false"

   r = get(HOST + URL_SERVICE + service_id)
   current_service_config = r.json()
   
   # can't upgrade a service if it's not in active state
   if current_service_config['state'] != "active":
      print "Service cannot be updated due to its current state: %s" % current_service_config['state']
      sys.exit(1)

   # Stuff the current service launch config into the request for upgrade
   upgrade_strategy['inServiceStrategy']['launchConfig'] = current_service_config['launchConfig']

   # post the upgrade request
   post(current_service_config['actions']['upgrade'], upgrade_strategy)

   print "Upgrade of %s service started!" % current_service_config['name']



#
# Script's entry point, starts Baker to execute the commands.
# Attempts to read environment variables to configure the program.
#
if __name__ == '__main__':
   import os
   if 'RANCHER_ACCESS_KEY' in os.environ:
      USERNAME = os.environ['RANCHER_ACCESS_KEY']

   if 'RANCHER_SECRET_KEY' in os.environ:
      PASSWORD = os.environ['RANCHER_SECRET_KEY']

   if 'RANCHER_URL' in os.environ:
      HOST = os.environ['RANCHER_URL']

   baker.run()

