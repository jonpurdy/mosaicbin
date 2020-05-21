from mosaicbin import feedbin
from mosaicbin import settings
from mosaicbin import functions

import pickle

from flask import Flask
from flask import request
from flask import render_template
from unidecode import unidecode

app = Flask(__name__)

# Loads the feeds first and ensures the user doesn't have to wait in case it needs to hit the API
use_cached = True
if use_cached:
    try:
        feeds_dict, tags = feedbin.get_cached_feeds_and_tags()
    except Exception as e:
        feeds_dict, tags = feedbin.get_feeds_and_tags_from_api()
else:
    feeds_dict, tags = feedbin.get_feeds_and_tags_from_api()


@app.route('/refresh')
def refresher():

    # gets them but doesn't need to do anything with the object, since it'll load it whens aved
    feeds_dict, tags = feedbin.get_feeds_and_tags_from_api()

    return render_template('refresh.html')

@app.route('/debug')
def debug():

    name='debug'

    feeds_dict, tags = feedbin.get_cached_feeds_and_tags()

    print_string = ""
    print_string += "Printing feeds_dict now...\n"
    print_string += "TAGS:"
    for tag in tags:
        print_string += "tag: %s, tags[tag]: %s" % (tag, tags[tag])
        print_string += "<p>"

    for feed in feeds_dict:
        print_string += "feed: %s, feeds_dict[feed]: %s" % (feed, vars(feeds_dict[feed]))
        print_string += "</p>"

    return render_template('base.html', name=name, print_string=print_string)


@app.route('/')
def root():

    feeds_dict, tags = feedbin.get_cached_feeds_and_tags()

    return render_template('index.html', feeds_dict=feeds_dict, tags=tags, display_unread=settings.display_unread_entries)


@app.route('/feed/<feed_id>')
@app.route('/feed/<feed_id>/titles')
def show_feed_titles(feed_id):

    # this is just to look up the feed name
    feeds_dict = feedbin.get_feeds()

    feed_obj = feeds_dict[int(feed_id)]

    try:
        #feed_name = subs_dict[int(feed_id)]        # old
        feed_name = feed_obj.title  # new
    except Exception as e:
        print(e)
        feed_name = "unknown, see show_feed_id"

    # now we start the real work
    unread = feedbin.get_all_unread_entries_list()

    per_page = 10000
    page_no = 1
    entries, total_count = feedbin.get_entries(feed_id, unread, per_page, int(page_no))

    if entries:

        return render_template('feed_entry_titles.html', feed_id=feed_id, feed_name=feed_name, entries=entries)
    
    else:

        return render_template('feed_no_entries.html', feed_id=feed_id, feed_name=feed_name)


@app.route('/feed/<feed_id>/entries/<entry_id>')
def show_entry(feed_id, entry_id):

    # this is just to look up the feed name
    feeds_dict = feedbin.get_feeds()
    feed_obj = feeds_dict[int(feed_id)]

    try:
        feed_name = feed_obj.title
    except Exception as e:
        print(e)
        feed_name = "unknown, see show_feed_id"

    entries = feedbin.get_single_entry(entry_id)

    if entries:
        clean_entries = functions.clean_entries(entries)

        return render_template('entry.html', feed_id=feed_id, feed_name=feed_name, entries=entries)
    
    else:

        return render_template('feed_no_entries.html', feed_id=feed_id, feed_name=feed_name)


@app.route('/entries/mark_as_read', methods=['POST'])
def mark_entries_as_read():

    # print_string = "<p>"
    entry_ids = []

    if request.form:

        # probably just not returning the first id for some reason, perhaps due to the hack
        for v in request.form:

            if 'entry_id' in v:
                print(v)
                #print_string += "%s " % request.form[v]
                entry_ids.append(request.form[v])
            # print("v: %s  PS: %s" % (v, print_string))
        result = feedbin.mark_entries_as_read(entry_ids)
    else:
        # print_string += "No entry IDs."
        result = []

    return render_template('marked_as_read.html', entry_ids=result, feed_id=request.form['feed_id'])