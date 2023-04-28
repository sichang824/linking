import daemon
import sys
import time
from pathlib import Path

from log import logger
from acm import YamlConfManager, CType
from watch_dog_patch import MacFSEventsObserver
from executer import SFTPEventHandler

from kyori2.host import RemoteHost


class MSyncConf(YamlConfManager):
    excludes = CType(list)
    includes = CType(list)
    executer = CType(dict)


c = MSyncConf("config/devcloud.yml")


def main():
    obs = MacFSEventsObserver()
    host = RemoteHost(c.remote_host,
                      c.remote_user,
                      port=c.remote_port,
                      pkey=c.remote_pkey)
    host.connect()
    for watch in c.watches:
        l_prefix, ld, r_prefix = watch.split(":")
        l_prefix = Path(l_prefix)
        r_prefix = Path(r_prefix)
        handler = SFTPEventHandler(
            (l_prefix / ld, r_prefix),
            host,
            c.excludes,
            c.ignore_patterns,
        )
        obs.schedule(handler, l_prefix / ld, recursive=True)

    obs.start()

    while host.check_connectivity():
        time.sleep(1)

    obs.stop()
    obs.join()
    host.close()


def run_daemon():
    normal = open('/Users/sichang/log/msync.log', "w+")
    error = open('/Users/sichang/log/msync.error.log', "w+")
    with daemon.DaemonContext(stderr=normal, stdout=error):
        while True:
            time.sleep(5)
            try:
                main()
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    # export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
    run_daemon()
