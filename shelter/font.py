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
"""Font and text rendering routines."""
import os

from sdl2 import rect, surface
from sdl2.ext.common import SDLError
from sdl2.ext.sprite import SoftwareSprite
import sdl2
from .util import memoize


class FontManager:
    DEFAULT_SIZE = (8, 16)
    DEFAULT_EXT = '.png'

    def __init__(self, path, size=None, ext=None):
        if size is None:
            size = self.DEFAULT_SIZE
        if ext is None:
            ext = self.DEFAULT_EXT
        self.size = size
        self.ext = ext
        self._path = path
        self._resources = sdl2.ext.Resources(path)
        self._bitmap_fonts = {}

    @property
    def path(self):
        return self._path

    @memoize('_bitmap_fonts')
    def create_bitmap_font(self, name):
        surface = self._load_bitmap(name)
        return BitmapFont(surface, self.size)

    def _load_bitmap(self, name):
        fname = '{name}{ext}'.format(name=name, ext=self.ext)
        path = self._resources.get_path(fname)
        return sdl2.ext.load_image(path)


class BitmapFont:
    """A bitmap graphics to character mapping.

    The BitmapFont class uses an image surface to find and render font
    character glyphs for text. It assumes the image surface has all
    characters from the ASCII standard in the correct order. Each character
    within each lines has the same size as specified by the size argument.

    """

    TABLE_SIZE = 256

    def __init__(self, imgsurface, size):
        """Creates a new BitmapFont instance from the passed image.

        Each character is expected to be of the same size (a 2-value tuple
        denoting the width and height) and to be in order of the table of
        characters of the ASCII standard.
        """
        if isinstance(imgsurface, SoftwareSprite):
            self.surface = imgsurface.surface
            self._sprite = imgsurface  # prevent GC on the Sprite
        elif isinstance(imgsurface, surface.SDL_Surface):
            self.surface = imgsurface
        self.size = size[0], size[1]
        self.offsets = self._calculate_offsets()

    def render(self, text, bpp=None):
        """Renders the passed text on a new Sprite and returns it."""
        lines = text.split(os.linesep)
        tw, th = self._calculate_text_size_from(lines)

        target_sprite = self._create_sprite_for_text(tw, th, bpp=bpp)
        self._blit_characters_on(target_sprite, lines)

        return target_sprite

    def render_on(self, imgsurface, text, offset=(0, 0)):
        """Renders a text on the passed sprite, starting at a specific
        offset.

        The top-left start position of the text will be the passed offset and
        4-value tuple with the changed area will be returned.
        """
        target = None
        if isinstance(imgsurface, SoftwareSprite):
            target = imgsurface.surface
        elif isinstance(imgsurface, surface.SDL_Surface):
            target = imgsurface
        else:
            raise TypeError('unsupported surface type')

        lines = text.split(os.linesep)
        tw, th = self._calculate_text_size_from(lines)

        self._blit_characters_on(target, lines, offset=offset)

        x, y = offset
        return (x, y, tw, th)

    def _calculate_offsets(self):
        """Calculates the internal character offsets."""
        w, h = self.surface.w, self.surface.h
        cw, ch = self.size

        assert (w * h) / (cw * ch) == self.TABLE_SIZE, \
            ('image surface for bitmap font is {}x{}, '
             'but characters have {}x{}'.format(w, h, cw, ch))

        chars_in_row = w // cw
        rows = h // ch

        offsets = []
        for i in range(rows):
            for j in range(chars_in_row):
                offset = rect.SDL_Rect(j * cw, i * ch, cw, ch)
                offsets.append(offset)
        assert len(offsets) == self.TABLE_SIZE

        return offsets

    def _blit_characters_on(self, target_sprite, lines, offset=None):
        """Blit each character on surface"""
        if offset:
            x, y = offset
        else:
            x, y = 0, 0

        cw, ch = self.size
        target = target_sprite.surface
        blit_surface = surface.SDL_BlitSurface
        fontsf = self.surface
        offsets = self.offsets

        for i, line in enumerate(lines):
            for j, char in enumerate(line):
                dstr = rect.SDL_Rect(x + j * cw, y + i * ch, 0, 0)
                offset = offsets[ord(char)]
                blit_surface(fontsf, offset, target, dstr)

    def _create_sprite_for_text(self, tw, th, bpp=None):
        # Create RGB Surface for text
        if bpp is None:
            bpp = self.surface.format.contents.BitsPerPixel
        sf = surface.SDL_CreateRGBSurface(0, tw, th, bpp, 0, 0, 0, 0)
        if not sf:
            raise SDLError()
        # Create software sprite from surface
        return SoftwareSprite(sf.contents, False)

    def _calculate_text_size_from(self, lines):
        tw, th = 0, 0
        w, h = self.size
        for line in lines:
            tw = max(tw, sum(w for c in line))
            th += h
        return tw, th
