from __future__ import annotations


class at_least:
    "An annotation to wrap around a value to describe that it is a minimum bound"

    def __init__(self, value) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"at least {self.value}"

    def __eq__(self, other) -> bool:
        try:
            return bool(self.value == other.value)
        except AttributeError:
            return False


class BaseIntrinsicSize:
    """Representation of the intrinsic size of an object.

    width: The width of the node.
    height: The height of the node.
    ratio: The height between height and width. width = height * ratio
    """

    def __init__(
        self,
        width: int | None = None,
        height: int | None = None,
        ratio: float | None = None,
        layout=None,
    ) -> None:
        self._layout = layout
        self._width = width
        self._height = height

        self._ratio: float | None = None

    def __repr__(self) -> str:
        return f"({self.width}, {self.height})"

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value) -> None:
        if self._width != value:
            self._width = value

            if self._layout:
                self._layout.dirty(intrinsic_width=value)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value) -> None:
        if self._height != value:
            self._height = value

            if self._layout:
                self._layout.dirty(intrinsic_height=value)

    @property
    def ratio(self):
        return self._ratio

    @ratio.setter
    def ratio(self, value) -> None:
        if self._ratio != value:
            self._ratio = value
            if self._layout:
                self._layout.dirty(intrinsic_ratio=value)
