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

import sdl2.ext
from shelter.font import BitmapFont
from shelter.renderer import SoftwareRenderSystem

__version__ = '0.1.0'

RESOURCES = sdl2.ext.Resources(__file__, '../res')


class Shelter:
    DEFAULT_FONTNAME = 'topaz8x16.png'

    def run(self):
        self._init_sdl()

        self.window = self._create_window()
        self.renderer = self._create_renderer_for(self.window)

        self.bitmap_font = self._create_bitmap_font()

        # Create a "hello world" text sprite
        self._write_hello_world()

        self._start_event_loop()

        return 0

    def _write_hello_world(self):
        text_sprite = self.bitmap_font.render(('Shelter v0.1\n'
                                               'This is a test'))
        self.renderer.render(text_sprite)

    def _start_event_loop(self):
        while True:
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    return
                elif event.type == sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                        return
            self.window.refresh()

    def _init_sdl(self):
        sdl2.ext.init()

    def _create_window(self):
        window = sdl2.ext.Window('Shelter', size=(800, 600))
        window.show()
        return window

    def _create_renderer_for(self, window):
        return SoftwareRenderSystem(window)

    def _create_bitmap_font(self, fontname=None):
        if not fontname:
            fontname = Shelter.DEFAULT_FONTNAME
        font_path = RESOURCES.get_path(fontname)
        bitmap_image = sdl2.ext.load_image(font_path)
        return BitmapFont(bitmap_image, size=(8, 16))
