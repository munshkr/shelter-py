import pytest
import os

from shelter.font import BitmapFont, FontManager


@pytest.fixture
def fonts_path():
    return os.path.join('res', 'fonts')


@pytest.fixture
def font_name():
    return 'topaz8x16'


def test_create_font_manager(fonts_path):
    manager = FontManager(fonts_path)
    assert manager.path == fonts_path
    assert manager.size == FontManager.DEFAULT_SIZE


def test_create_bitmap_font_from_manager(fonts_path, font_name):
    manager = FontManager(fonts_path)
    bitmap = manager.create_bitmap_font(font_name)
    assert isinstance(bitmap, BitmapFont)