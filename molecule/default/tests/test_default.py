from glob import glob
import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_services_running_and_enabled(host):
    service = host.service('munin-node')
    assert service.is_running
    assert service.is_enabled


# Munin relies on cron to gather stats at regular intervals bit cron isn't
# enabled by default in docker, and in any case we don't want to wait.
# Instead delete the generated files and manually run an update
def test_gather_stats(host):
    for f in glob('/var/www/html/munin/*.html'):
        os.remove(f)

    with host.sudo('munin'):
        out = host.check_output('/usr/bin/munin-cron')
    assert len(out) == 0

    assert host.file('/var/www/html/munin/system-day.html').exists
