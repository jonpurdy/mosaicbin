
import mosaicbin
import mosaicbin.feedbin as feedbin
from mosaicbin import settings
from mosaicbin import functions
import os

global creds

def setup():

    try:
        creds = (str(os.environ['FEEDBIN_USERNAME']), str(os.environ['FEEDBIN_PASSWORD']))
    except Exception as e:
        print("Credentials not available. Run:\nexport FEEDBIN_USERNAME='whatever'\nexport FEEDBIN_PASSWORD='whatever'\n")
        exit()

def test_get_single_entry():

    global entries

    # gets a single known entry from feedbin API
    # specifically, feedbin ID 2446256855 = https://mjtsai.com/blog/2019/09/02/privilegedhelpertools-and-checking-xpc-peers/
    entries = feedbin.get_single_entry("2446256855")

    # entry should be returned in a single item list
    assert type(entries) == list
    assert len(entries) == 1

    # single item list, so just use that from now on
    entry = entries[0]

    # verify that the fields are the same as before
    # if this fails, perhaps the Feedbin API has changed
    expected_keys = ['id', 'feed_id', 'title', 'author', 'summary', 'content', 'url', 'extracted_content_url', 'published', 'created_at']
    for k in entry:
        if k in expected_keys:
            assert True
        else:
            assert False

    # verify that these fields are correct and haven't changed
    assert entry['id'] == 2446256855
    assert entry['title'] == 'Security Flaws in Adobe Acrobat Reader'
    assert entry['author'] == 'Michael Tsai'


# can run the tests by calling this file directly for debugging
def main():
    test_get_single_entry()


if __name__ == '__main__':
    main()