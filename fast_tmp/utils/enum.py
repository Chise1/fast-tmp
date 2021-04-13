import enum


class Promise:
    """
    Base class for the proxy class created in the closure of the lazy function.
    It's used to recognize promises in code.
    """

    pass


__all__ = ["IntEnumType", "CharEnumType"]


class ChoicesMeta(enum.EnumMeta):
    """A metaclass for creating a enum choices."""

    def __new__(metacls, classname, bases, classdict):
        labels = []
        for key in classdict._member_names:
            value = classdict[key]
            if (
                isinstance(value, (list, tuple))
                and len(value) > 1
                and isinstance(value[-1], (Promise, str))
            ):
                *value, label = value
                value = tuple(value)
            else:
                label = key.replace("_", " ").title()
            labels.append(label)
            # Use dict.__setitem__() to suppress defenses against double
            # assignment in enum's classdict.
            dict.__setitem__(classdict, key, value)
        cls = super().__new__(metacls, classname, bases, classdict)
        cls._value2label_map_ = dict(zip(cls._value2member_map_, labels))
        # Add a label property to instances of enum which uses the enum member
        # that is passed in as "self" as the value to use when looking up the
        # label in the choices.
        cls.label = property(lambda self: cls._value2label_map_.get(self.value))
        cls.do_not_call_in_templates = True
        return enum.unique(cls)

    def __contains__(cls, member):
        if not isinstance(member, enum.Enum):
            # Allow non-enums to match against member values.
            return any(x.value == member for x in cls)
        return super().__contains__(member)

    @property
    def names(cls):
        empty = ["__empty__"] if hasattr(cls, "__empty__") else []
        return empty + [member.name for member in cls]

    @property
    def choices(cls):
        empty = [(None, cls.__empty__)] if hasattr(cls, "__empty__") else []
        t = empty + [(member.value, member.label) for member in cls]
        ret = {}
        for i in t:
            ret[i[0]] = i[1]
        return ret

    @property
    def labels(cls):
        return [label for _, label in cls.choices]

    @property
    def values(cls):
        return [value for value, _ in cls.choices]


# class Choices(enum.Enum, metaclass=ChoicesMeta):
#     """Class for creating enumerated choices."""
#
#     def __str__(self):
#         """
#         Use value when cast to str, so that Choices set as model instance
#         attributes are rendered as expected in templates and similar contexts.
#         """
#         return str(self.value)


class IntEnumType(enum.IntEnum, metaclass=ChoicesMeta):
    """Class for creating enumerated integer choices."""

    pass


class CharEnumType(str, enum.Enum, metaclass=ChoicesMeta):
    """Class for creating enumerated string choices."""

    def _generate_next_value_(name, start, count, last_values):
        return name
