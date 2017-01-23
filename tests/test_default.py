import testinfra.utils.ansible_runner

from glob import glob
from os import remove

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


def test_services_running_and_enabled(Service):
    service = Service('munin-node')
    assert service.is_running
    assert service.is_enabled


# Munin relies on cron to gather stats at regular intervals bit cron isn't
# enabled by default in docker, and in any case we don't want to wait.
# Instead delete the generated files and manually run an update
def test_gather_stats(Command, File, Sudo):
    for f in glob('/var/www/html/munin/*.html'):
        remove(f)

    with Sudo('munin'):
        out = Command.check_output('/usr/bin/munin-cron')
    assert len(out) == 0

    assert File('/var/www/html/munin/system-day.html').exists
