# Shelter - ASCII/ANSI art drawing tool
# Copyright (C) 2018  Damián Silvani
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from abc import ABC, abstractmethod


class Widget(ABC):
    def __init__(self):
        self._sprite = None
        self._children = set()
        self.dirty = True

    def add_child(self, widget):
        """Add a child widget

        Arguments:
            widget {Widget} -- child widget

        Returns:
            Widget -- self
        """

        self._children.add(widget)
        return self

    def remove_child(self, widget):
        """Remove a child widget

        Arguments:
            widget {Widget} -- child widget

        Returns:
            Widget -- self
        """

        self._children.remove(widget)
        return self

    def render(self):
        """Render sprite to be rendered

        Widget subclasses need to implement the `draw` method instead.

        The sprite is generated only when the `dirty` flag is on. It is the
        responsability of the widget to toggle the dirty flag when the sprite
        needs to be rebuilt.

        Returns:
            SoftwareSprite -- widget sprite
        """

        if self.dirty:
            self._sprite = self.draw()
            self.dirty = False
        return self._sprite

    @abstractmethod
    def draw(self):
        """Create sprite to be rendered

        Widget subclasses need to implement this widget for rendering.

        Returns:
            SoftwareSprite -- widget sprite
        """

        raise NotImplementedError
