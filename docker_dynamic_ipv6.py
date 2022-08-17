#!/usr/bin/env python3

import ipaddress
import json
import os
import shutil
import subprocess
from logging import info, error

def get_global_ipv6(interface):
    '''
    Uses Unix 'ip' utility to get primary global system IPv6 address information

    :param interface string: Name of the interface which IPv6 address should be returned
    :returns dict: Return dict style in the -json notation of the 'ip' output
    '''
    info('Checkinf if \'ip\' system utility is installed')
    if shutil.which('ip') is None:
        error('Unix tool \'ip\' is not installed')
        return None
    info('Getting IPv6 output for global addresses from system')
    output = subprocess.run([
            'ip','-6','-json',
            'address','show',
            'dev',args.interface,
            'scope','global'],
        capture_output=True)
    if output.returncode != 0:
        error('Error while running system \'ip\' utility')
        error(output.stderr)   
        return None
    return json.loads(output.stdout)

def docker_sys_prefix_same(docker_config_file, sys_ipv6_net):
    '''
    Compares prefix saved in the docker config and the prefix of the given IPv6

    :param docker_config_file string: Path to docker config file
    :param sys_ipv6_net ipv6network: System IPv6 network
    :returns boolean:
    '''
    if not os.path.exists(docker_config_file):
        error('Docker config file %s does not exist' %(docker_config_file))
        return None
    with open(docker_config_file, 'r') as f:
        docker_config = json.load(f)
    docker_prefix = docker_config['']
    system_prefix = ipaddress
    if docker_prefix == system_prefix:
        info('Provided prefix is the same as the one in the config')
        return True
    else:
        info('Provided prefix is NOT the same as the one in the config')
        return False

def update_docker_prefix(docker_config_file, sys_ipv6_net):
    '''
    Updates the docker deamon config file with the provided sys_ipv6_net

    :param docker_config_file string: Path to docker config file
    :param sys_ipv6_net ipv6network: System IPv6 network
    :returns None:
    '''
    if not os.path.exists(docker_config_file):
        error('Docker config file %s does not exist' %(docker_config_file))
        return None
    with open(docker_config_file, 'r') as f:
        docker_config = json.load(f)
    docker_config['fixed-cidr-v6'] = str(sys_ipv6_net)
    info('Writing new IPv6 prefix to docker config')
    with open(docker_config_file, 'w') as f:
        json.dump(docker_config, f, indent=4, sort_keys=True)

def restart_docker():
    '''
    Restarts docker daemon

    :returns None:
    '''
    info('Restarting docker daemon')
    output = subprocess.run(['systemctl','restart','docker'], capture_output=True)
    if output.returncode != 0:
        error('Error while restarting docker daemon')
        error(output.stderr)   
    else:
        info('Docker daemon restarted successfully')

if __name__ == '__main__':
    import argparse
    import logging

    DOCKER_CONFIG_FILE = '/etc/docker/daemon.json'

    parser = argparse.ArgumentParser(description='Tool to check if IPv6 prefix changed and update docker with the new one')
    parser.add_argument('-i', '--interface', required=True, help='Interface of which the IPv6 prefix should be taken')
    parser.add_argument('-d', '--dockerconfig', default=DOCKER_CONFIG_FILE, help='Path to the docker deamon config: Default %s' %(DOCKER_CONFIG_FILE))
    args = parser.parse_args()

    ipv6_info = get_global_ipv6(args.interface)
    if ipv6_info is None:
        exit(1)

    validity = 0
    for addr_info in ipv6_info['addr_info']:
        if validity < addr_info['valid_live_time']:
            validity = addr_info['valid_live_time']
            sys_ipv6_net = ipaddress.IPv6Network('%s/%s' %(add_info[local], addr_info['prefixlen']), strict=False)

    if not docker_sys_prefix_same(args.dockerconfig, sys_ipv6_net):
        update_docker_prefix(args.dockerconfig, sys_ipv6_net)
        restart_docker()