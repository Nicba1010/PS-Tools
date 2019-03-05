from copy import deepcopy

from yaml import Dumper, YAMLObject


class YamlDumpable(YAMLObject):
    def __init__(self):
        self.test = "test"
        self.test2 = "test2"
        self.get = "get"

    @classmethod
    def to_yaml(cls, dumper, data):
        new_data = deepcopy(data)
        print(new_data.__dict__)
        for item in ['test']:
            print(new_data.__dict__)
            del new_data.__dict__[item]
        return dumper.represent_yaml_object('test3', new_data, cls)
