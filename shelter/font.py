"""Font and text rendering routines."""
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
import os

from sdl2 import pixels, rect, surface
from sdl2.ext.color import Color, convert_to_color
from sdl2.ext.common import SDLError
#from sdl2.ext.compat import *
from sdl2.ext.sprite import SoftwareSprite

_HASSDLTTF = True
try:
    from sdl2 import sdlttf
except ImportError:
    _HASSDLTTF = False

__all__ = ["BitmapFont"]


class BitmapFont(object):
    """A bitmap graphics to character mapping.

    The BitmapFont class uses an image surface to find and render font
    character glyphs for text. It assumes the image surface has all
    characters from the ASCII standard in the correct order. Each character
    within each lines has the same size as specified by the size argument.

    """

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

    def _calculate_offsets(self):
        """Calculates the internal character offsets."""
        w, h = self.surface.w, self.surface.h
        cw, ch = self.size

        assert (w * h) / (cw * ch) == 256, \
            ('image surface for bitmap font is {}x{}, '
             'but characters have {}x{}'.format(w, h, cw, ch))

        chars_in_row = w // cw
        rows = h // ch

        offsets = []
        for i in range(rows):
            for j in range(chars_in_row):
                offset = rect.SDL_Rect(j * cw, i * ch, cw, ch)
                offsets.append(offset)
        assert len(offsets) == 256

        return offsets

    def render(self, text, bpp=None):
        """Renders the passed text on a new Sprite and returns it."""
        tw, th = 0, 0
        w, h = self.size

        # Calculate text width and height
        lines = text.split(os.linesep)
        for line in lines:
            tw = max(tw, sum([w for c in line]))
            th += h

        # Create RGB Surface for text
        if bpp is None:
            bpp = self.surface.format.contents.BitsPerPixel
        sf = surface.SDL_CreateRGBSurface(0, tw, th, bpp, 0, 0, 0, 0)
        if not sf:
            raise SDLError()

        # Create software sprite from surface
        imgsurface = SoftwareSprite(sf.contents, False)
        target = imgsurface.surface
        blit_surface = surface.SDL_BlitSurface
        fontsf = self.surface
        offsets = self.offsets

        # Blit each character on surface
        dstr = rect.SDL_Rect(0, 0, 0, 0)
        y = 0
        for line in lines:
            dstr.y = y
            x = 0
            for c in line:
                dstr.x = x
                offset = offsets[ord(c)]
                blit_surface(fontsf, offset, target, dstr)
                x += w
            y += h

        return imgsurface

    def render_on(self, imgsurface, text, offset=(0, 0)):
        """Renders a text on the passed sprite, starting at a specific
        offset.

        The top-left start position of the text will be the passed offset and
        4-value tuple with the changed area will be returned.
        """
        w, h = self.size

        target = None
        if isinstance(imgsurface, SoftwareSprite):
            target = imgsurface.surface
        elif isinstance(imgsurface, surface.SDL_Surface):
            target = imgsurface
        else:
            raise TypeError("unsupported surface type")

        lines = text.split(os.linesep)
        blit_surface = surface.SDL_BlitSurface
        fontsf = self.surface
        offsets = self.offsets

        dstr = rect.SDL_Rect(0, 0, 0, 0)
        y = offset[1]
        for line in lines:
            dstr.y = y
            x = offset[0]
            for c in line:
                dstr.x = x
                if c in offsets:
                    blit_surface(fontsf, offsets[c], target, dstr)
                # elif c != ' ':

                #    TODO: raise an exception for unknown char?
                x += w
            y += h
        return (offset[0], offset[1], x + w, y + h)
