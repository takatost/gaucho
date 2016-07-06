#!/usr/bin/env python
import baker
import json
import requests
import sys
import time

HOST = "http://rancher.local:8080"
URL_SERVICE = "/services/"
USERNAME = "userid"
PASSWORD = "password"

def get(url):
   r = requests.get(url, auth=(USERNAME, PASSWORD))
   r.raise_for_status()
   return r

def post(url, data):
   if data:
      r = requests.post(url, data=json.dumps(data), auth=(USERNAME, PASSWORD))
   else:
      r = requests.post(url, data="", auth=(USERNAME, PASSWORD))
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
@baker.command(params={
                        "service_id": "The ID of the service to upgrade.", 
                        "start_first": "Whether or not to start the new instance first before stopping the old one.",
                        "complete_previous": "If set and the service was previously upgraded but the upgrade wasn't completed, it will be first marked as Finished and then the upgrade will occur.",
                        "imageUuid": "If set the config will be overwritten to use new image. Don't forget Rancher Formatting 'docker:<Imagename>:tag'"
                       })
def upgrade(service_id, start_first=True, complete_previous=False, imageUuid=None,
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
   
   # complete previous upgrade flag on
   if complete_previous and current_service_config['state'] == "upgraded":
      print "Previous service upgrade wasn't completed, completing it now..."
      post(HOST + URL_SERVICE + service_id + "?action=finishupgrade", "")
      r = get(HOST + URL_SERVICE + service_id)
      current_service_config = r.json()

      sleep_count = 0
      while current_service_config['state'] != "active" and sleep_count < 60:
         print "Waiting for upgrade to finish..."
         time.sleep (2)
         r = get(HOST + URL_SERVICE + service_id)
         current_service_config = r.json()
         sleep_count += 1
      
   # can't upgrade a service if it's not in active state
   if current_service_config['state'] != "active":
      print "Service cannot be updated due to its current state: %s" % current_service_config['state']
      sys.exit(1)

   # Stuff the current service launch config into the request for upgrade
   upgrade_strategy['inServiceStrategy']['launchConfig'] = current_service_config['launchConfig']

   if imageUuid != None:
      # place new image into config
      upgrade_strategy['inServiceStrategy']['launchConfig']['imageUuid'] = imageUuid
      print "New Image: %s" % upgrade_strategy['inServiceStrategy']['launchConfig']['imageUuid']

   # post the upgrade request
   post(current_service_config['actions']['upgrade'], upgrade_strategy)

   print "Upgrade of %s service started!" % current_service_config['name']



#
# Script's entry point, starts Baker to execute the commands.
# Attempts to read environment variables to configure the program.
#
if __name__ == '__main__':
   import os

   # support for new Rancher agent services
   # http://docs.rancher.com/rancher/latest/en/rancher-services/service-accounts/
   if 'CATTLE_ACCESS_KEY' in os.environ:
      USERNAME = os.environ['CATTLE_ACCESS_KEY']

   if 'CATTLE_SECRET_KEY' in os.environ:
      PASSWORD = os.environ['CATTLE_SECRET_KEY']

   if 'CATTLE_URL' in os.environ:
      HOST = os.environ['CATTLE_URL']

   if 'RANCHER_ACCESS_KEY' in os.environ:
      USERNAME = os.environ['RANCHER_ACCESS_KEY']

   if 'RANCHER_SECRET_KEY' in os.environ:
      PASSWORD = os.environ['RANCHER_SECRET_KEY']

   if 'RANCHER_URL' in os.environ:
      HOST = os.environ['RANCHER_URL']

   # make sure host ends with v1 
   if not HOST.endswith ('/v1'):
      HOST = HOST + '/v1'


   baker.run()

