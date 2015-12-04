import os
import platform
from subprocess import Popen, PIPE
import utils

SUPPORTED = ['arch', 'debian', 'ubuntu', 'centos', 'fedora']


class PasswordHaijacker(object):
    """Main class"""
    def __init__(self):
        pass

    def execute_command(self, command):
        process = Popen(command, shell=True, stdout=PIPE, stdin=PIPE).communicate()[0]
        res = process.decode("utf-8").splitlines()
        return res        

    def get_interfaces(self):
        return self.execute_command('ls /sys/class/net')
        

    def get_networks(self):
        return self.execute_command('ip r | grep -v default | awk \'{print $1}\'')

    def get_hosts(self, network):
        return self.execute_command("nmap -sP %s | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'" % network)
        

def print_list(list_):
    """Helper function to print list."""
    count = 0
    for item in list_:
        count+=1
        print('%s) %s' % (count, item))

def main():
    ph = PasswordHaijacker()
    sep = '***********************************'
    welcome_message = """%s\nWelcome to the password hijacker.\n\n%s\n\nFolow the instructions.\n
Note that package autoinstall not tested on dpkg-based distributions.\n""" % (sep, sep)
    print(welcome_message)
    print('Checking dependencies\n')
    dependencies = utils.Dependencies()
    if not dependencies.all_installed():
        install = input('Not all dependencies are installed. Do you want to install them automaticly? [Y/n]\t') or 'y'
        if install.lower() == 'n':
            exit(1)
        else:
            dependencies.install()        
    print('Scanning network interfaces.\n')
    interfaces = ph.get_interfaces()
    print_list(interfaces)
    interface = int(input('\nSelect your interface.\t'))-1
    print('Selected interface: %s\n' % interface)  
    print('Scanning networks.\n')
    networks = ph.get_networks()
    print_list(networks)
    network = networks[int(input('\nSelect your network.\t'))-1]
    print('Selected network: %s\n' % network) 
    print('Scanning selected network...')
    hosts = ph.get_hosts(network)
    print_list(hosts)
    hosts_number = input('Select hosts separeted with commas. "*" for all\t')
    hosts_number = hosts_number.split(',') if '*' not in hosts else '*'
    selected_hosts = []
    if hosts_number[0] != '*':
        for host in hosts_number:
            selected_hosts.append(hosts[int(host)-1])
    else:
        selected_hosts = hosts        
    print(selected_hosts)

if __name__ == '__main__':
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

    if not platform.linux_distribution(supported_dists = SUPPORTED)[0]:
        exit('Your distribution is not supported yet. \nSorry :(')

    main()        