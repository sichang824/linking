# https://developer.apple.com/documentation/coreservices/1455361-fseventstreameventflags/kfseventstreameventflaguserdropped#declaration

import enum

# from executer import *


class MacEventFlags(enum.Enum):
    DELETED  = 0x200  # 删除
    RENAMED  = 0x800  # 重命名  （移动）
    ATTR_MOD = 0x8000 # 属性修改
    MODIFIED = 0x1000 # 内容修改
    META_MOD = 0x400  # 元数据修改
    CREATED  = 0x100  # 创建


# class MacEventFlags:
#     DIR_CREATED = [131328]
#     DIR_MOVED = [133120, 189696]
#     DIR_DELETED = [131584, 132608, 131840, 133376]
#     DIR_PROP_CHANGED = [132096, 132352]
#     # 文件标识
#     FILE_MOVED = [67584, 67840, 71936, 88320, 87296, 119040, 120064, 119808]
#     FILE_CREATED = [65792, 69888]
#     FILE_DELETED = [
#         66048, 66304, 67072, 72704, 71424, 87808, 72960, 68096, 89344, 120576,
#         119552
#     ]
#     FILE_MODIFIED = [70656, 70912, 88064]
#     FILE_PROP_CHANGED = [66560, 66816]
#     FILE_COPIED = [4277504]

#     SYSTEM_LINK_CREATED = [262400]
#     SYSTEM_LINK_DELETED = [262656]

# class SFTPEventExecuters(enum.EnumMeta):
#     DIR_CREATED = SFTPDirCreated
#     DIR_MOVED = SFTPDirMoved
#     DIR_DELETED = SFTPDirDeleted
#     DIR_PROP_CHANGED = SFTPDirPropChanged
#     DIR_COPIED = SFTPDirCopied
#     FILE_MOVED = SFTPFileMoved
#     FILE_CREATED = SFTPFileCreated
#     FILE_DELETED = SFTPFileDeleted
#     FILE_MODIFIED = SFTPFileModified
#     FILE_PROP_CHANGED = SFTPFilePropChanged
#     SYSTEM_LINK_CREATED = SFTPSysLinkCreated
#     SYSTEM_LINK_DELETED = SFTPSysLinkDeleted