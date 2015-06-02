#!/usr/bin/env python

import os
import sys

from boto.swf.layer1 import Layer1
from boto.swf import regions
import yaml

"""
Here are the typical structures of domains, workflow types and activity types,
as returned by "describe_*" methods of the boto.swf API, represented as Python
objects dumps.

Domain:

    {
        u'domainInfo': {
            u'status': u'REGISTERED',
            u'name': u'TestDomain'
        },
        u'configuration': {
            u'workflowExecutionRetentionPeriodInDays': u'30'
        }
    }

Workflow Type:

    {
        u'configuration': {
            u'defaultExecutionStartToCloseTimeout': u'3600',
            u'defaultTaskStartToCloseTimeout': u'30',
            u'defaultTaskList': {
                u'name': u'test'
            },
            u'defaultChildPolicy': u'TERMINATE'
        },
        u'typeInfo': {
            u'status': u'REGISTERED',
            u'creationDate': 1389710910.635,
            u'workflowType': {
                u'version': u'1.0',
                u'name': u'GreeterWorkflow.greet'
            }
        }
    }

Activity Type:

    {
        u'configuration': {
            u'defaultTaskStartToCloseTimeout': u'0',
            u'defaultTaskScheduleToStartTimeout': u'0',
            u'defaultTaskList': {
                u'name': u'None'
            },
            u'defaultTaskScheduleToCloseTimeout': u'0',
            u'defaultTaskHeartbeatTimeout': u'0'
        },
        u'typeInfo': {
            u'status': u'REGISTERED',
            u'creationDate': 1417521580.65,
            u'activityType': {
                u'version': u'2.0',
                u'name': u'ActivityName.foo'
            }
        }
    }

"""
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
