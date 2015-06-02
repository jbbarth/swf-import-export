#!/usr/bin/env python

import os
import sys

from swf.querysets import domain
from boto.swf import regions
import yaml

"""
Here are the typical structures of domains, workflow types and activity types,
as returned by "describe_*" methods of the boto.swf API, represented as Python
objects dumps.

NB: this is *not* what you will find in the serialized version as we now use
simple-workflow and it re-maps all those attributes to a flatter structure.

TODO: document attributes in the new simple-workflow format

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
REGION = os.getenv("SWF_REGION", "us-east-1")
DEBUG = os.getenv("DEBUG", False)

#utility functions
def debug(msg):
    if DEBUG:
        sys.stderr.write("DEBUG: {}\n".format(msg))


#real work against SWF API
result = []

for domain in domain.DomainQuerySet(region=REGION).all():
    debug(domain)
    domain_result = {
        "name": domain.name,
        "status": domain.status,
        "retention_period": domain.retention_period,
    }
    domain_result["workflows"] = []
    domain_result["activities"] = []
    #workflows
    for workflow_type in domain.workflows():
        debug(workflow_type)
        domain_result["workflows"].append({
            "execution_timeout": workflow_type.execution_timeout,
            "decision_tasks_timeout": workflow_type.decision_tasks_timeout,
            "task_list": workflow_type.task_list,
            "child_policy": workflow_type.child_policy,
            "status": workflow_type.status,
            "creation_date": workflow_type.creation_date,
            "version": workflow_type.version,
            "name": workflow_type.name,
        })
    #activities
    for activity_type in domain.activities():
        debug(activity_type)
        domain_result["activities"].append({
            "task_schedule_to_start_timeout": activity_type.task_schedule_to_start_timeout,
            "task_schedule_to_close_timeout": activity_type.task_schedule_to_close_timeout,
            "task_start_to_close_timeout": activity_type.task_start_to_close_timeout,
            "task_list": activity_type.task_list,
            "task_heartbeat_timeout": activity_type.task_heartbeat_timeout,
            "status": activity_type.status,
            "creation_date": activity_type.creation_date,
            "version": activity_type.version,
            "name": activity_type.name,
        })
    #wrap up
    result.append(domain_result)

#output yaml tree
print yaml.safe_dump(result)
