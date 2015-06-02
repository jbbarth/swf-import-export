#!/usr/bin/env python

import os
import sys

from boto.swf.layer1 import Layer1
from boto.swf import regions
import yaml

#parameters through environment
STATUS = os.getenv("SWF_REGISTRATION_STATUS", "REGISTERED")
REGION = os.getenv("SWF_REGION", "us-east-1")
DEBUG = os.getenv("DEBUG", False)

#utility functions
def debug(msg):
    if DEBUG:
        sys.stderr.write("DEBUG: {}\n".format(msg))

#find region to connect to
try:
    region_object = filter(lambda r: r.name == REGION, regions())[0]
except IndexError:
    sys.stderr.write("Error: unable to find region named '{}', exiting.\n".format(REGION))
    sys.exit(1)

#real work against SWF API
swf = Layer1(region=region_object)
result = []

domains = swf.list_domains(registration_status=STATUS)
for hsh in domains["domainInfos"]:
    domain_name = hsh["name"]
    domain = swf.describe_domain(domain_name)
    debug("Domain: {}".format(domain))
    domain_result = domain.copy()
    domain_result["workflowTypes"] = []
    domain_result["activityTypes"] = []
    #workflows
    workflow_types = swf.list_workflow_types(domain_name, registration_status=STATUS)
    for hsh in workflow_types["typeInfos"]:
        workflow_type = swf.describe_workflow_type(
            domain_name,
            hsh["workflowType"]["name"],
            hsh["workflowType"]["version"],
        )
        domain_result["workflowTypes"].append(workflow_type.copy())
        debug("  Workflow Type: {}".format(workflow_type))
    #activities
    activity_types = swf.list_activity_types(domain_name, registration_status=STATUS)
    for hsh in activity_types["typeInfos"]:
        activity_type = swf.describe_activity_type(
            domain_name,
            hsh["activityType"]["name"],
            hsh["activityType"]["version"],
        )
        domain_result["activityTypes"].append(activity_type.copy())
        debug("  Activity Type: {}".format(activity_type))
    #wrap up
    result.append(domain_result)

#output yaml tree
print yaml.safe_dump(result)
