import yaml
from typing import Any
from pathlib import Path
from log import logger


class ConfigurationNoRaw(Exception):

    def __init__(self) -> None:
        msg = "No configuration in raw."
        super().__init__(msg)


class ConfigurationNamingConflict(Exception):

    def __init__(self, *args) -> None:
        msg = f"Configuration naming conflict: {args}."
        super().__init__(msg)


class ConfigurationTypeInvalid(Exception):

    def __init__(self, expect, actual) -> None:
        e = expect.__name__ if isinstance(expect, object) else expect
        a = actual.__name__ if isinstance(actual, object) else actual
        msg = f"Configuration type is invalid, expect:{e}, actual:{a}."
        super().__init__(msg)


class ConfigurationType:

    def __init__(self, _type) -> None:
        self._type = _type


CType = ConfigurationType


class BaseConfModel:

    def __getattr__(self, name: str) -> Any:
        if name in self.__dict__:
            raise ConfigurationNamingConflict(name)
        return self.get(name)

    def __getattribute__(self, name: str) -> Any:
        thing = object.__getattribute__(self, name)

        if isinstance(thing, ConfigurationType):
            conf = self.get(name)
            if not isinstance(conf, thing._type):
                raise ConfigurationTypeInvalid(thing._type, type(conf))
            else:
                return conf

        if not thing: return self.get(name)
        return thing


class BaseConfManager(BaseConfModel):
    __origin = {}

    def __init__(self, path) -> None:
        self.path = Path(path)
        self.__origin = self.load()

    def get(self, name):
        if not self.__origin:
            raise ConfigurationNoRaw
        return self.__origin.get(name, {})

    def load(self):
        pass

    def load_from_local(self):
        pass

    def load_from_remote(self):
        pass


class YamlConfManager(BaseConfManager):

    def load(self):
        return yaml.safe_load(self.path.open("r"))


class ConfTemplate(YamlConfManager):
    excludes = CType(list)
    includes = CType(list)


def main():
    conf = ConfTemplate("./devcloud.yml")
    logger.log(conf.excludes)
    logger.log(conf.includes)
    logger.log(conf.executer)


if __name__ == "__main__":
    main()