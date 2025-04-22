import pytest
from library_item import LibraryItem

def test_default_values():
    item = LibraryItem("Song", "Artist")
    assert item.rating == 0
    assert item.play_count == 0

def test_rating_clamping():
    assert LibraryItem("Song", "Artist", rating=6).rating == 5
    assert LibraryItem("Song", "Artist", rating=-1).rating == 0

def test_play_count_non_negative():
    assert LibraryItem("Song", "Artist", play_count=-5).play_count == 0

def test_rating_type_cast():
    assert LibraryItem("Song", "Artist", rating="3").rating == 3

def test_play_count_type_cast():
    assert LibraryItem("Song", "Artist", play_count="2").play_count == 2

def test_info_formatting():
    item = LibraryItem("Hello", "Adele", rating=3)
    assert item.info() == "Hello - Adele ***"

def test_star_generation():
    assert LibraryItem("X", "Y", rating=4).stars() == "****"
