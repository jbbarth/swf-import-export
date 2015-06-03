SWF Import / Export
===================

A simple tool to manage your SWF structures from different domains / environments.


Install
-------

For now this project is only distributed as a source repo (no egg), so clone this repository,
and install the dependencies with:

    pip install -r requirements.txt

(maybe in a virtualenv if you like to isolate things)


Export domains: dump.py
-----------------------

The `dump.py` script allows you to dump domains in YAML format:

    $ ./dump.py
    # => will write YAML to stdout

It accepts the following parameters through environment variables

|  Variable      |     Description                                                                              |
|----------------|----------------------------------------------------------------------------------------------|
| DEBUG          | If set (to "1" for instance), debug messages will be written to stderr.                      |
| SWF_REGION     | The region you want to work on. Defaults to `boto.swf`'s default region, us-east-1.          |
| SWF_DOMAIN     | A specific domain to retrieve. Defaults to "all domains in this region".                     |

So a more complete example could look like:

    $ SWF_REGION=eu-west-1 SWF_DOMAIN=my.domain ./dump.py > data/dump_eu-west-1_my_domain.yml


