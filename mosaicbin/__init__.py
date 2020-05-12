from mosaicbin import feedbin
from mosaicbin import settings
from mosaicbin import functions

from flask import Flask
from flask import request
from flask import render_template
from unidecode import unidecode

app = Flask(__name__)

@app.route('/test')
def test():
    name='test'
    return render_template('base.html', name=name)

#global subs_dict # delete later, thanks codefactor

@app.route('/')
def root():

    subs_dict, feeds_dict, tags = feedbin.get_subs_and_tags()

    # We need this to initialize the print_string properly
    print_string = ""

    # Let's get Pages out of the way first
    print_string += "<h1>Pages</h1>"
    print_string += "<p>"
    for feed_id in feeds_dict:
        if feeds_dict[feed_id].title == "Pages":
            print_string += "<a href='feed/%s/titles'>View list of articles saved to Feedbin Pages</a> %s </br>" % (feed_id, feeds_dict[feed_id].unread_count)
    print_string += "</p>"

    for tag in tags:
        print_string += "<h1>%s</h1>" % tag
        print_string += "<p>"
        for feed_id in tags[tag]:
            # need to look up the feed name using subs_dict, now feeds_dict

            # only print the feed name if there are unread entries
            if feeds_dict[feed_id].unread_count > 0:
                print_string += "<a href='feed/%s/1'>%s</a> <a href='feed/%s/titles'>(list)</a> %s </br>" % (feed_id, feeds_dict[feed_id].title, feed_id, feeds_dict[feed_id].unread_count)
            else:
                if settings.display_unread_entries:
                    print_string += "<a href='feed/%s/1'>%s</a> <a href='feed/%s/titles'>(list)</a> %s </br>" % (feed_id, feeds_dict[feed_id].title, feed_id, feeds_dict[feed_id].unread_count)

        print_string += "</p>"

    # added to deal with subs that have no tags
    # credit K Trueno
    if len(tags) < 1:
        print_string += "<h1>All Feeds</h1>"
        print_string += "<p>"
        for feed in feeds_dict:
            print_string += "<a href='feed/%s/1'>%s</a> %s </br>" % (feed_id, feeds_dict[feed_id].title, feeds_dict[feed_id].unread_count)

    return render_template('base.html', print_string=print_string)


@app.route('/feed/<feed_id>/<page_no>')
def show_feed_id(feed_id, page_no):

    import math 

    per_page = settings.entries_per_page

    # this is just to look up the feed name
    subs_dict, feeds_dict = feedbin.get_subs_dict()

    try:
        #feed_name = subs_dict[int(feed_id)]        # old
        feed_name = feeds_dict[int(feed_id)].title  # new
    except Exception as e:
        print(e)
        feed_name = "unknown, see show_feed_id"

    # now we start the real work
    unread = feedbin.get_all_unread_entries_list()

    entries, total_count = feedbin.get_entries(feed_id, unread, per_page, int(page_no))

    # if len(entries) > 0: # delete later, thanks codefactor
    if entries:
        
        clean_entries = functions.clean_entries(entries)
        page_count = math.ceil(total_count / per_page)

        return render_template('feed.html', feed_id=feed_id, feed_name=feed_name, entries=clean_entries, per_page=per_page, page_no=page_no, page_count=page_count)
    
    else:

        return render_template('feed_no_entries.html', feed_id=feed_id, feed_name=feed_name)



@app.route('/feed/<feed_id>/titles')
def show_feed_titles(feed_id):

    # this is just to look up the feed name
    subs_dict, feeds_dict = feedbin.get_subs_dict()

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
    subs_dict, feeds_dict = feedbin.get_subs_dict()

    feed_obj = feeds_dict[int(feed_id)]

    try:
        #feed_name = subs_dict[int(feed_id)]        # old
        feed_name = feed_obj.title  # new
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

    print("REQUESTFORM2: %s" % request.form)

    # commented way back in 2019
    # print_string += "...marked as read.</p><p><a href='/feed/%s/%s'>Go back!</a></p>" % (request.form['feed_id'], request.form['current_page'])
    # print("PS before return: %s" % print_string)
    

    # commented 2020-05-12 to remove current_page
    # return render_template('marked_as_read.html', entry_ids=result, feed_id=request.form['feed_id'], current_page=request.form['current_page'])
    return render_template('marked_as_read.html', entry_ids=result, feed_id=request.form['feed_id'])