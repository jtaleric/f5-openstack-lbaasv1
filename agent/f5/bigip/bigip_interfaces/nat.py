import os
from f5.common import constants as const

from f5.bigip.bigip_interfaces import domain_address
from f5.bigip.bigip_interfaces import icontrol_folder

# Networking - Self-IP
from neutron.common import log


class NAT(object):
    def __init__(self, bigip):
        self.bigip = bigip

        # add iControl interfaces if they don't exist yet
        self.bigip.icontrol.add_interface('LocalLB.NATV2')

        # iControl helper objects
        self.lb_nat = self.bigip.icontrol.LocalLB.NATV2

    @icontrol_folder
    @domain_address
    @log.log
    def create(self, name=None, ip_address=None, orig_ip_address=None,
               traffic_group=None, vlan_name=None, folder='Common'):
        if not self.exists(name=name, folder=folder):
            if not traffic_group:
                traffic_group = const.SHARED_CONFIG_DEFAULT_TRAFFIC_GROUP
            VLAN_filter_list = self.lb_nat.typefactor.create(
                                           'Common.VLANFilterList')
            VLAN_filter_list.state = self.lb_nat.typefactory.create(
                                           'Common.EnabledState').STATE_ENABLED
            VLAN_filter_list.vlans = [vlan_name]
            self.lb_nat.create([name],
                               [orig_ip_address],
                               [ip_address],
                               [vlan_name],
                               [traffic_group],
                               [VLAN_filter_list])
            return True
        else:
            return False

    @icontrol_folder
    def delete(self, name=None, folder='Common'):
        if self.exists(name=name, folder=folder):
            self.lb_nat.delete_nat([name])
            return True
        else:
            return False

    @icontrol_folder
    def get_all(self, folder='Common'):
        return self.lb_nat.get_list()

    @icontrol_folder
    def get_addrs(self, folder='Common'):
        return map(os.path.basename,
                   self.lb_nat.get_translation_address(
                            self.get_all(folder=folder)))

    @icontrol_folder
    def get_addr(self, name=None, folder='Common'):
        if self.exists(name=name, folder=folder):
            return self.lb_nat.get_translation_address(
                                                 [name])[0]

    @icontrol_folder
    def get_original_addrs(self, folder='Common'):
        return map(os.path.basename,
                   self.lb_nat.get_origin_address(
                            self.get_all(folder=folder)))

    @icontrol_folder
    def get_original_addr(self, name=None, folder='Common'):
        if self.exists(name=name, folder=folder):
            return self.lb_nat.get_origin_address(
                                                 [name])[0]

    @icontrol_folder
    def get_vlan(self, name=None, folder='Common'):
        self.lb_nat.get_vlan([name])[0]

    @icontrol_folder
    def exists(self, name=None, folder='Common'):
        if name in self.lb_nat.get_list():
            return True