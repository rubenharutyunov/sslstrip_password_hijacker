"""
Utils
"""
import platform
from password_hijacker import SUPPORTED
from subprocess import Popen, PIPE, call

DEPENDENCIES = ['nmap', 'sslstrip', 'dsniff']

class Dependencies(object):
    """Installs script dependencies"""
    def __init__(self, deps=DEPENDENCIES):
        self.deps = deps
        self.distr = platform.linux_distribution(supported_dists = SUPPORTED)[0]
        self.package_manager = PackageAutoinstall(self.distr)
        
    def install(self):
        for dep in self.deps:
            self.package_manager.check_and_install(dep)

    def all_installed(self):
        ok = True
        for dep in self.deps:    
            if self.package_manager.installed(dep) != ok:
                ok = False
        return ok


class PackageAutoinstall(object):
    """Package management in supported distros"""
    def __init__(self, distr):
        self.distr = distr
        
        self.commands = {
            'arch' : {
                'install' : 'pacman -Sy --noconfirm',
                'check' : 'pacman -Q | grep'
            },
            'debian' : {
                'install' : 'apt-get install -qq --force-yes',
                'check' : 'dpkg -s'
            },
            'ubuntu' : {
                'install' : 'apt-get install -qq --force-yes',
                'check' : 'dpkg -s'
            },
            'centos': {
                'install' : 'yum -y install',
                'check' : 'rpm -qa | grep'
            },     
            'fedora': {
                'install' : 'yum -y install',
                'check' : 'rpm -qa | grep'
            }, 
        }

    def installed(self, packagename):
        """
        Returns True when package is installed. False otherwise.
        """
        command = '%s %s' % (self.commands.get(self.distr).get('check'), packagename)
        process = Popen(command, shell=True, stdout=PIPE, stdin=PIPE).communicate()[0]
        if process:
            return True    
        return False    

    def install(self, packagename):   
        command = '%s %s' % (self.commands.get(self.distr).get('install'), packagename)
        call(command, shell=True)

    def check_and_install(self, packagename):
        if not self.installed(packagename):
            print('***\n%s not installed\n***\n' % packagename)
            print('***\nInstalling %s\n***\n' % packagename)
            self.install(packagename)    
        else:    print('%s aleady installed' % packagename)    

if __name__ == '__main__':
    #print(PackageAutoinstall('centos').check_and_install('nmap')) 
    print(Dependencies(['nmap', 'sslstrip']).all_installed()      )