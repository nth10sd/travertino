from __future__ import annotations


class Viewport:
    """
    A viewport is a description of surface onto which content will be
    rendered. It stores the size of the surface(in pixels), plus the
    pixel density of the viewport.
    """

    def __init__(self, width: int = 0, height: int = 0, dpi: int | None = None) -> None:
        self.width = width
        self.height = height
        self.dpi = dpi


class BaseBox:
    """Describe the layout of a box displaying a node.

    Stored properties
    ~~~~~~~~~~~~~~~~~
    visible: The node is included in rendering, and is visible. A value of
        False indicates the node takes up space, but is not rendered.

    content_width: The width of the content in the box
    content_height: The height of the content in the box
    content_top: The top position of the content in the box, relative to the box
    content_left: The left position of the content in the box, relative to the box
    content_bottom: The distance from the bottom of the content to the bottom of the box
    content_right: The distance from the right of the content to the right of the box

    origin_top: The absolute position of the top of the box
    origin_left: The absolute position of the left of the box

    Computed properties
    ~~~~~~~~~~~~~~~~~~~
    width: The overall width of the box
    height: The overall height of the box

    absolute_content_top: The absolute position of the top of the content box.
    absolute_content_left: The absolute position of the left of the content box.
    absolute_content_bottom: The absolute position of the bottom of the content box.
    absolute_content_right: The absolute position of the right of the content box.

    """

    def __init__(self, node) -> None:
        self.node = node
        self._reset()

    def __repr__(self) -> str:
        return "<{} ({}x{} @ {},{})>".format(
            self.__class__.__name__,
            self.content_width,
            self.content_height,
            self.absolute_content_left,
            self.absolute_content_top,
        )

    def _reset(self) -> None:
        # Some properties describing whether this node exists in
        # layout *at all*.
        self.visible = True

        # Width and height of the content box.
        self.content_width = 0
        self.content_height = 0

        # Box position, relative to the containing box
        self._content_top = 0
        self._content_left = 0
        self.content_bottom = 0
        self.content_right = 0

        self.__origin_top = 0
        self.__origin_left = 0

        # Set the origin via properties; this forces the calculation of
        # absolute positions.
        self._origin_top = 0
        self._origin_left = 0

    ######################################################################
    # Origin handling
    ######################################################################
    @property
    def _origin_top(self) -> int:
        return self.__origin_top

    @_origin_top.setter
    def _origin_top(self, value: int) -> None:
        if value != self.__origin_top:
            self.__origin_top = value
            for child in self.node.children:
                if child.layout:
                    child.layout._origin_top = self.absolute_content_top

    @property
    def _origin_left(self) -> int:
        return self.__origin_left

    @_origin_left.setter
    def _origin_left(self, value: int) -> None:
        if value != self.__origin_left:
            self.__origin_left = value
            for child in self.node.children:
                if child.layout:
                    child.layout._origin_left = self.absolute_content_left

    @property
    def width(self) -> int:
        return self._content_left + self.content_width + self.content_right

    @property
    def height(self) -> int:
        return self._content_top + self.content_height + self.content_bottom

    ######################################################################
    # Content box properties
    ######################################################################
    @property
    def content_top(self) -> int:
        return self._content_top

    @content_top.setter
    def content_top(self, value: int) -> None:
        self._content_top = value
        for child in self.node.children:
            if child.layout:
                child.layout._origin_top = self.absolute_content_top

    @property
    def content_left(self) -> int:
        return self._content_left

    @content_left.setter
    def content_left(self, value: int) -> None:
        self._content_left = value
        for child in self.node.children:
            if child.layout:
                child.layout._origin_left = self.absolute_content_left

    ######################################################################
    # Absolute content box position
    ######################################################################

    @property
    def absolute_content_top(self) -> int:
        return self.__origin_top + self._content_top

    @property
    def absolute_content_right(self) -> int:
        return self.__origin_left + self._content_left + self.content_width

    @property
    def absolute_content_bottom(self) -> int:
        return self.__origin_top + self._content_top + self.content_height

    @property
    def absolute_content_left(self) -> int:
        return self.__origin_left + self._content_left
