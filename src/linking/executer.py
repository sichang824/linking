from pathlib import Path
import re
from constants import MacEventFlags

from log import logger
from kyori2.host import Local


class BaseSFTPExecuter(Local):

    def skip(self, *args):
        logger.info(f"The File is fine, no need to touch it. {args}")

    def mkdir(self, path):
        try:
            self.sftp.stat(str(path))
        except:
            self.ssh.exec_command(f"mkdir -p '{str(path)}'")

        logger.info(f"mkdir {str(path)}")
        return True

    def move(self, src, dst):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(
                f"mv '{str(src)}' '{str(dst)}'")
            assert stdout.channel.recv_exit_status() == 0
            logger.info(f"move {str(src)} -> {str(dst)}")
            return True
        except:
            logger.warn(f"move failed {str(src)} -> {str(dst)}")
            return False

    def remove(self, path):

        if not self.is_exists(path):
            logger.warn("Will skip unknown path.")
            return True

        try:
            self.ssh.exec_command(f"rm -rf '{str(path)}'")
            logger.info(f"remove {str(path)}")
            return True
        except:
            logger.warn(f"remove failed {str(path)}")
            return False

    def touch(self, path):
        if not self.is_exists(path.parent):
            self.mkdir(path.parent)

        try:
            self.ssh.exec_command(f"touch '{str(path)}'")
        except:
            pass

    def put(self, src, dst):

        if not self.is_exists(dst.parent):
            self.mkdir(dst.parent)

        if self.checksum(src, dst):
            self.skip(src, dst)
            return False

        try:
            self.sftp.put(str(src), str(dst))
            logger.info(f"put file {str(src)} -> {str(dst)}")
            return True
        except Exception:
            logger.warn(f"put file failed {str(src)} -> {str(dst)}")
            return False

    def is_exists(self, path):
        try:
            self.sftp.stat(str(path))
            return True
        except:
            return False


class SFTPEventHandler(BaseSFTPExecuter):

    def __init__(self, prefix, host, excludes=[], ignore_patterns=[]):
        self.prefix = prefix
        self.host = host
        self.ssh = self.host.ssh
        self.sftp = self.host.sftp
        self.excludes = excludes
        self.ignore_patterns = [re.compile(i) for i in ignore_patterns]

    # @property
    # def ssh(self):
    #     return self.host.ssh

    # @property
    # def sftp(self):
    #     return self.host.sftp

    def get_remote_path(self, path):
        return Path(
            str(path).replace(str(self.prefix[0]), str(self.prefix[1])))

    def get_src_path(self, event):
        return Path(event.native_event.path)

    def get_dst_path(self, event):
        return Path(event.dst_event.path)

    def on_created(self, event):
        logger.debug("目标被创建")
        lp = self.get_src_path(event)
        rp = self.get_remote_path(lp)

        if event.native_event.is_file:
            self.put(lp, rp)

    def on_deleted(self, event):
        logger.debug("目标被删除")

        lp = self.get_src_path(event)
        rp = self.get_remote_path(lp)
        self.remove(rp)

    def on_meta_mod(self, event):
        logger.debug("目标元数据被修改")

    def on_renamed(self, event):
        logger.debug("目标被重命名")
        lp = self.get_src_path(event)
        srp = self.get_remote_path(lp)

        if event.dst_event:
            dp = self.get_dst_path(event)
            drp = self.get_remote_path(dp)

            if event.dst_event and not self.move(srp, drp):
                if event.native_event.is_file:
                    self.put(dp, drp)
                else:
                    self.on_modified(event)
        else:
            self.remove(srp)

    def on_modified(self, event):
        logger.debug("目标内容被修改")
        lp = self.get_src_path(event)

        if event.native_event.is_file:
            rp = self.get_remote_path(lp)
            self.put(lp, rp)
        else:
            for item in Path(lp).rglob("**/*"):
                if not item.is_file(): continue
                rp = self.get_remote_path(str(item))
                self.put(item, rp)

    def on_attr_mod(self, event):
        logger.debug("目标属性被修改")

    def dispatch(self, event):

        if not self.host.connected:
            logger.warn(f"Remote host is not connected. {self.host}")
            return

        if self.excludes:
            for p in self.excludes:
                if p in event.native_event.path: return

        if self.ignore_patterns:
            for p in self.ignore_patterns:
                if re.findall(p, event.native_event.path): return
                if event.dst_event and re.findall(p, event.dst_event.path):
                    return
        try:
            if event.flag == MacEventFlags.CREATED:
                self.on_created(event)

            if event.flag == MacEventFlags.DELETED:
                self.on_deleted(event)

            if event.flag == MacEventFlags.RENAMED:
                self.on_renamed(event)

            if event.flag == MacEventFlags.MODIFIED:
                self.on_modified(event)

            if event.flag == MacEventFlags.ATTR_MOD:
                self.on_attr_mod(event)

            if event.flag == MacEventFlags.META_MOD:
                self.on_meta_mod(event)
        except Exception as e:
            logger.error(f"Executer handle failed: {e}")