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

    try:
        while True:
            if not host.connected:
                try:
                    host.connect()
                except Exception as e:
                    logger.error(f"Remote {host} connect failed: {e}")

            try:
                host.check_connectivity()
            except Exception as e:
                logger.error(f"Remote {host} connect no connectivity: {e}")

            time.sleep(60)
    except KeyboardInterrupt:
        obs.stop()
        obs.join()
        sys.exit()


def run_daemon():
    normal = open('/Users/sichang/log/msync.log', "w+")
    error = open('/Users/sichang/log/msync.error.log', "w+")
    with daemon.DaemonContext(stderr=normal, stdout=error):
        main()


if __name__ == "__main__":
    # export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
    run_daemon()
