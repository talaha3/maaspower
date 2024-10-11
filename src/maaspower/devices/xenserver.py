"""
xenserver.py
"""

import paramiko
from dataclasses import dataclass
from typing import Annotated as A
from typing import Literal

from maaspower.maas_globals import desc
from maaspower.maasconfig import RegexSwitchDevice


@dataclass(kw_only=True)
class XenServer(RegexSwitchDevice):
    """A device controlled via a Xenserver hypervisor"""

    name: A[
        str, desc("Logical device name for VM provisioned by XenServer hypervisor")
    ]
    hostname: A[str, desc("Hostname of the XenServer hypervisor")]
    username: A[str, desc("Username for the XenServer hypervisor")]
    password: A[str, desc("Password for the XenServer hypervisor")]
    on: A[str, desc("command line string to switch device on")]
    off: A[str, desc("command line string to switch device off")]
    query: A[str, desc("command line string to query device state")]
    query_on_regex: A[str, desc("match the on status return from query")] = "^running$"
    query_off_regex: A[str, desc("match the off status return from query")] = "^halted$"

    type: Literal["XenServer"] = "XenServer"

    def __post_init__(self):
        """
        Create the 'device' variable, containing properties for establishing \n
        an SSH connection via paramiko.
        """

        super().__post_init__()
        self.device = {
            "username": self.username,
            "password": self.password,
        }
    
    def establish_ssh_connection_and_execute_command(self, command: str):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.hostname ,**self.device)
        stdout, stderr = ssh.exec_command(command)
        print(stdout.read().decode(), stderr.read().decode())
        ssh.close()
        return stdout.read().decode()

    def turn_on(self):
        self.establish_ssh_connection_and_execute_command(self.on)

    def turn_off(self):
        self.establish_ssh_connection_and_execute_command(self.off)

    def run_query(self) -> str:
        return self.establish_ssh_connection_and_execute_command(self.query)
