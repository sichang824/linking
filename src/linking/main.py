import daemon
import socket
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


def telnet(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, int(port)))
        s.settimeout(1)
        s.shutdown(2)
        return 1
    except Exception as e:
        logger.log(f'{port} is down')
        return 0


def main():
    obs = MacFSEventsObserver()
    host = RemoteHost(c.remote_host,
                      c.remote_user,
                      port=c.remote_port,
                      pkey=c.remote_pkey)
    host.initial()

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
            if not host.check_connectivity():
                host.close()
            if not host.connected and not host.initial():
                logger.error(f"Remote host connect failed: {host}")
            time.sleep(1)
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
