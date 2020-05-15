
import mosaicbin
import mosaicbin.feedbin as feedbin
from mosaicbin import settings
from mosaicbin import functions
import os

global creds

def setup():

    pass # nothing needed here for now

def test_clean_entries_generic():

    # test an entry that should work just fine
    entries = [{'id': 24123456789, 'feed_id': 1, 'title': 'Test Title', 'author': 'Mosaicbin', 'summary': 'Brief summary Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation.', 'content': '<p><a href="https://github.com/jonpurdy/mosaicbin">Mosaicbin</a></p><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation.</p>', 'url': 'https://github.com/jonpurdy/mosaicbin', 'extracted_content_url': 'https://extract.feedbin.com/parser/feedbin/some_generic_hash', 'published': '2020-05-14T19:09:08.000000Z', 'created_at': '2020-05-14T19:09:39.881881Z'}]

    cleaned_entries = mosaicbin.functions.clean_entries(entries)

    # verify the input is correct (a list)
    assert type(entries) == list

    # verify the output type is correct (a list)
    assert type(cleaned_entries) == list

    # verify that the number of cleaned entries is the same as the input
    assert len(entries) == len(cleaned_entries)

def test_clean_entries_date():

    # published date is cleaned correctly?
    entries = [{'id': 24123456789, 'feed_id': 1, 'title': 'blank', 'author': 'blank', 'summary': 'blank', 'content': 'blank', 'url': 'blank', 'extracted_content_url': 'blank', 'published': '2020-05-14T19:09:08.000000Z', 'created_at': '2020-05-14T19:09:39.881881Z'}]
    cleaned_entries = mosaicbin.functions.clean_entries(entries)
    assert cleaned_entries[0]['published_human_readable'] == "2020-05-14 19:09:08 UTC"

def test_clean_entries_none_content():

    # if content is None, ensure it returns a "no content" string
    entries = [{'id': 24123456789, 'feed_id': 1, 'title': 'blank', 'author': 'blank', 'summary': 'blank', 'content': None, 'url': 'blank', 'extracted_content_url': 'blank', 'published': '2020-05-14T19:09:08.000000Z', 'created_at': '2020-05-14T19:09:39.881881Z'}]
    cleaned_entries = mosaicbin.functions.clean_entries(entries)
    assert cleaned_entries[0]['content'] == "Mosaicbin: no content."

def test_clean_entries_image():

    # ensure it processes the image if present
    entries = [{'id': 24123456789, 'feed_id': 1, 'title': 'blank', 'author': 'blank', 'summary': 'blank', 'content': '<p><img src="https://raw.githubusercontent.com/jonpurdy/mosaicbin/master/mosaicbin/static/icon64.gif"></p>', 'url': 'blank', 'extracted_content_url': 'blank', 'published': '2020-05-14T19:09:08.000000Z', 'created_at': '2020-05-14T19:09:39.881881Z'}]
    cleaned_entries = mosaicbin.functions.clean_entries(entries)
    assert cleaned_entries[0]['content'] == "Mosaicbin: no content."


# can run the tests by calling this file directly for debugging
def main():
    setup()
    test_clean_entries_generic()
    test_clean_entries_date()
    test_clean_entries_none_content()

if __name__ == '__main__':
    main()