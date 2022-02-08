from __future__ import annotations

from .colors import Color, color, hsl, hsla, rgb, rgba


class Choices:
    "A class to define allowable data types for a property"

    def __init__(
        self,
        *constants,
        default: bool = False,
        string: bool = False,
        integer: bool = False,
        number: bool = False,
        color: bool = False,
    ) -> None:
        self.constants = set(constants)
        self.default = default

        self.string = string
        self.integer = integer
        self.number = number
        self.color = color

        self._options = sorted(str(c).lower().replace("_", "-") for c in self.constants)
        if self.string:
            self._options.append("<string>")
        if self.integer:
            self._options.append("<integer>")
        if self.number:
            self._options.append("<number>")
        if self.color:
            self._options.append("<color>")

    def validate(
        self, value
    ) -> Color | hsl | hsla | rgb | rgba | float | int | str | None:
        if self.default:
            if value is None:
                return None
        if self.string:
            try:
                return value.strip()
            except AttributeError:
                pass
        if self.integer:
            try:
                return int(value)
            except (ValueError, TypeError):
                pass
        if self.number:
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
        if self.color:
            try:
                return color(value)
            except ValueError:
                pass
        if value == "none":
            value = None
        for const in self.constants:
            if value == const:
                return const

        raise ValueError(f"'{value}' is not a valid initial value")

    def __str__(self) -> str:
        return ", ".join(self._options)


class BaseStyle:
    """A base class for style declarations.

    Exposes a dict-like interface.
    """

    _PROPERTIES = {}
    _ALL_PROPERTIES = {}

    def __init__(self, **style) -> None:
        self._applicator = None
        self.update(**style)

    ######################################################################
    # Interface that style declarations must define
    ######################################################################

    def apply(self, property, value) -> None:
        raise NotImplementedError(
            "Style must define an apply method"
        )  # pragma: no cover

    ######################################################################
    # Provide a dict-like interface
    ######################################################################

    def reapply(self) -> None:
        for style in self._PROPERTIES.get(self.__class__, set()):
            self.apply(style, getattr(self, style))

    def update(self, **styles) -> None:
        "Set multiple styles on the style definition."
        for name, value in styles.items():
            name = name.replace("-", "_")
            if name not in self._ALL_PROPERTIES.get(self.__class__, set()):
                raise NameError("Unknown style '%s'" % name)

            setattr(self, name, value)

    def copy(self, applicator=None):
        "Create a duplicate of this style declaration."
        dup = self.__class__()
        dup._applicator = applicator
        for style in self._PROPERTIES.get(self.__class__, set()):
            try:
                setattr(dup, style, getattr(self, "_%s" % style))
            except AttributeError:
                pass
        return dup

    def __getitem__(self, name: str) -> None:
        name = name.replace("-", "_")
        if name in self._PROPERTIES.get(self.__class__, set()):
            return getattr(self, name)
        raise KeyError(name)

    def __setitem__(self, name: str, value: str) -> None:
        name = name.replace("-", "_")
        if name in self._PROPERTIES.get(self.__class__, set()):
            setattr(self, name, value)
        else:
            raise KeyError(name)

    def __delitem__(self, name: str) -> None:
        name = name.replace("-", "_")
        if name in self._PROPERTIES.get(self.__class__, set()):
            delattr(self, name)
        else:
            raise KeyError(name)

    def items(self):
        result = []
        for name in self._PROPERTIES.get(self.__class__, set()):
            try:
                result.append((name, getattr(self, "_%s" % name)))
            except AttributeError:
                pass
        return result

    def keys(self):
        result = set()
        for name in self._PROPERTIES.get(self.__class__, set()):
            if hasattr(self, "_%s" % name):
                result.add(name)
        return result

    ######################################################################
    # Get the rendered form of the style declaration
    ######################################################################
    def __str__(self) -> str:
        non_default = []
        for name in self._PROPERTIES.get(self.__class__, set()):
            try:
                non_default.append(
                    (name.replace("_", "-"), getattr(self, "_%s" % name))
                )
            except AttributeError:
                pass

        return "; ".join(f"{name}: {value}" for name, value in sorted(non_default))

    @classmethod
    def validated_property(
        cls, name: str, choices: Choices, initial: str | int | None = None
    ):
        "Define a simple validated property attribute."
        try:
            initial_ = choices.validate(initial)
        except ValueError:
            raise ValueError(f"Invalid initial value '{initial}' for property '{name}'")

        def getter(self):
            return getattr(self, "_%s" % name, initial_)

        def setter(self, value) -> None:
            try:
                value = choices.validate(value)
            except ValueError:
                raise ValueError(
                    "Invalid value '{}' for property '{}'; Valid values are: {}".format(
                        value, name, choices
                    )
                )

            if value != getattr(self, "_%s" % name, initial_):
                setattr(self, "_%s" % name, value)
                self.apply(name, value)

        def deleter(self) -> None:
            try:
                value = getattr(self, "_%s" % name, initial_)
                delattr(self, "_%s" % name)
                if value != initial_:
                    self.apply(name, initial_)
            except AttributeError:
                # Attribute doesn't exist
                pass

        cls._PROPERTIES.setdefault(cls, set()).add(name)
        cls._ALL_PROPERTIES.setdefault(cls, set()).add(name)
        setattr(cls, name, property(getter, setter, deleter))

    @classmethod
    def directional_property(cls, name):
        "Define a property attribute that proxies for top/right/bottom/left alternatives."

        def getter(self):
            return (
                getattr(self, name % "_top"),
                getattr(self, name % "_right"),
                getattr(self, name % "_bottom"),
                getattr(self, name % "_left"),
            )

        def setter(self, value) -> None:
            if isinstance(value, tuple):
                if len(value) == 4:
                    setattr(self, name % "_top", value[0])
                    setattr(self, name % "_right", value[1])
                    setattr(self, name % "_bottom", value[2])
                    setattr(self, name % "_left", value[3])
                elif len(value) == 3:
                    setattr(self, name % "_top", value[0])
                    setattr(self, name % "_right", value[1])
                    setattr(self, name % "_bottom", value[2])
                    setattr(self, name % "_left", value[1])
                elif len(value) == 2:
                    setattr(self, name % "_top", value[0])
                    setattr(self, name % "_right", value[1])
                    setattr(self, name % "_bottom", value[0])
                    setattr(self, name % "_left", value[1])
                elif len(value) == 1:
                    setattr(self, name % "_top", value[0])
                    setattr(self, name % "_right", value[0])
                    setattr(self, name % "_bottom", value[0])
                    setattr(self, name % "_left", value[0])
                else:
                    raise ValueError(
                        "Invalid value for '{}'; value must be an number, or a 1-4 tuple.".format(
                            name % ""
                        )
                    )
            else:
                setattr(self, name % "_top", value)
                setattr(self, name % "_right", value)
                setattr(self, name % "_bottom", value)
                setattr(self, name % "_left", value)

        def deleter(self) -> None:
            delattr(self, name % "_top")
            delattr(self, name % "_right")
            delattr(self, name % "_bottom")
            delattr(self, name % "_left")

        cls._ALL_PROPERTIES.setdefault(cls, set()).add(name % "")
        setattr(cls, name % "", property(getter, setter, deleter))

    # def list_property(name, choices, initial=None):
    #     "Define a property attribute that accepts a list of independently validated values."
    #     initial = choices.validate(initial)

    #     def getter(self):
    #         return getattr(self, '_%s' % name, initial)

    #     def setter(self, values):
    #         try:
    #             value = [choices.validate(v) for v in values.split(',')]
    #         except ValueError:
    #             raise ValueError("Invalid value in for list property '%s'; Valid values are: %s" % (
    #                 name, choices
    #             ))

    #         if value != getattr(self, '_%s' % name, initial):
    #             setattr(self, '_%s' % name, value)
    #             self.apply(name, value)

    #     def deleter(self):
    #         try:
    #             delattr(self, '_%s' % name)
    #             self.apply(name, value)
    #         except AttributeError:
    #             # Attribute doesn't exist
    #             pass

    #     _PROPERTIES.add(name)
    #     return property(getter, setter, deleter)
