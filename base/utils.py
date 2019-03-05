from logging import Logger
from typing import Any, List, Union

from .errors import InvalidFileConstantException


def constant_check(logger: Logger, name: str, constant: Any, valid: Union[Any, List[Any]]):
    if (constant in valid) if isinstance(valid, List) else constant == valid:
        logger.info(f'{name}: {constant}')
    else:
        raise InvalidFileConstantException(name, constant, valid)


metadic = {}


def _generatemetaclass(bases, metas, priority):
    trivial = lambda m: sum([issubclass(M, m) for M in metas], m is type)
    # hackish!! m is trivial if it is 'type' or, in the case explicit
    # metaclasses are given, if it is a superclass of at least one of them
    metabs = tuple([mb for mb in map(type, bases) if not trivial(mb)])
    metabases = (metabs + metas, metas + metabs)[priority]
    if metabases in metadic:  # already generated metaclass
        return metadic[metabases]
    elif not metabases:  # trivial metabase
        meta = type
    elif len(metabases) == 1:  # single metabase
        meta = metabases[0]
    else:  # multiple metabases
        metaname = "_" + ''.join([m.__name__ for m in metabases])
        meta = classmaker()(metaname, metabases, {})
    return metadic.setdefault(metabases, meta)


def classmaker(*metas, **options):
    """Class factory avoiding metatype conflicts. The invocation syntax is
    makecls(M1,M2,..,priority=1)(name,bases,dic). If the base classes have
    metaclasses conflicting within themselves or with the given metaclasses,
    it automatically generates a compatible metaclass and instantiate it.
    If priority is True, the given metaclasses have priority over the
    bases' metaclasses"""

    priority = options.get('priority', False)  # default, no priority
    return lambda n, b, d: _generatemetaclass(b, metas, priority)(n, b, d)
