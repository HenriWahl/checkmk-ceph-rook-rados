#!/usr/bin/env python3
#
# Replacement for librados which is not reachable for Checkmk plugin if Ceph runs in Kubernetes Cluster
#
# ©2022 henri.wahl@ukdd.de

from json import dumps, loads
from subprocess import run

# command to get into rook ceph tools container and run 'ceph'
CEPH_COMMAND = 'kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- ceph'
# hostname template for Ceph nodes and their appearance in Checkmk
CEPH_HOSTNAME_TEMPLATE = 'ceph-cluster-'

class Rados:
    """
    Dummy class for Checkmk ceph plugin
    """
    
    def __init__(self, **kwargs):
        """
        Dummy init - no need for initialization
        """
    
    def run_cli_command(self, command_json, timeout=5):
        """
        Run command in Ceph CLI
        """      
        # every commmand comes in key 'prefix' - sometimes contains multiple keywords
        command = loads(command_json)['prefix'].split(' ')
        # some command comes extra keyword 
        if loads(command_json).get('detail'):
            command += [loads(command_json).get('detail')]
        command_as_list = CEPH_COMMAND.split(' ') +\
                          ['-f', 'json', '--connect-timeout', str(timeout)] + command
        result = run(command_as_list, capture_output=True)
        return_code = result.returncode
        # kick off newlines
        result_json = result.stdout.strip()
        # because 'quorum_names' key in JSON does not contain actual hostnames but 'a', 'b', 'c'
        # this has to be fixed to make Checkmk happy
        # comes from Ceph Rook and might have to be adjusted
        if b'"quorum_names":' in result_json:
            quorum_names_hostnames = []
            result_dict = loads(result_json)
            for quorum_name in result_dict['quorum_names']:
                #
                # Here some local adjustment and fantasy is required.
                # Depending on the naming scheme in your environment you might need to adjust this to
                # get real hostnames instead of 'a', 'b' and 'c' etc.
                #
                # derive host number from quorum name - 97 is the ascii number of 'a'
                quorum_names_hostnames.append(f'{CEPH_HOSTNAME_TEMPLATE}{ord(quorum_name)-96}')
            result_dict['quorum_names'] = quorum_names_hostnames
            result_json = dumps(result_dict)

        return return_code, result_json
    
    def connect(self):
        """
        Dummy connect method - just to be compatible with Checkmk ceph plugin
        No connect needed because using kubectl + rook
        """
    
    def mon_command(self, command, inbuf=b'', timeout=5):
        """
        https://docs.ceph.com/en/latest/rados/api/python/#rados.Rados.mon_command
        """
        return self.run_cli_command(command)

    def mgr_command(self, command, inbuf=b'', timeout=5):
        """
        https://docs.ceph.com/en/latest/rados/api/python/#rados.Rados.mgr_command
        """
        return self.run_cli_command(command)


# Debugging
if __name__ == '__main__':
    rados = Rados()
    rados.connect()
    print(rados.mon_command(dumps({"prefix": "status", "format": "json"})))
