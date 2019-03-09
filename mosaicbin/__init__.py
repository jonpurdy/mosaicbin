from mosaicbin import feedbin

from flask import Flask
from flask import request
from flask import render_template
from unidecode import unidecode

app = Flask(__name__)

@app.route('/test')
def test():
    name='test'
    return render_template('base.html', name=name)

global subs_dict

@app.route('/')
def root():

    subs_dict, tags = feedbin.get_subs_and_tags()

    print_string = ""
    for tag in tags:
        print_string += "<h1>%s</h1>" % tag
        print_string += "<p>"
        for feed_id in tags[tag]:
            # need to look up the feed name using subs_dict
            print_string += "<a href='feed/%s/1'>%s</a></br>" % (feed_id, subs_dict[feed_id])
        print_string += "</p>"

    return render_template('base.html', print_string=print_string)


@app.route('/feed/<feed_id>/<page_no>')
def show_feed_id(feed_id, page_no):

    import math 

    per_page = 3

    # this is just to look up the feed name
    subs_dict = feedbin.get_subs_dict()
    feed_name = subs_dict[int(feed_id)]

    # now we start the real work
    unread = feedbin.get_all_unread_entries()

    entries, total_count = feedbin.get_entries(feed_id, unread, per_page, int(page_no))

    if len(entries) > 0:
        
        clean_entries = feedbin.clean_entries(entries)
        page_count = math.ceil(total_count / per_page)

        return render_template('feed.html', feed_id=feed_id, feed_name=feed_name, entries=clean_entries, per_page=per_page, page_no=page_no, page_count=page_count)
    
    else:

        return render_template('feed_no_entries.html', feed_id=feed_id, feed_name=feed_name)




@app.route('/entries/mark_as_read', methods=['POST'])
def mark_entries_as_read():

    print_string = "<p>"
    entry_ids = []

    if len(request.form) > 0:

        # probably just not returning the first id for some reason, perhaps due to the hack
        for v in request.form:

            if 'entry_id' in v:
                print(v)
                #print_string += "%s " % request.form[v]
                entry_ids.append(request.form[v])
            print("v: %s  PS: %s" % (v, print_string))
        result = feedbin.mark_entries_as_read(entry_ids)
    else:
        print_string += "No entry IDs."
        result = []

    # print_string += "...marked as read.</p><p><a href='/feed/%s/%s'>Go back!</a></p>" % (request.form['feed_id'], request.form['current_page'])
    # print("PS before return: %s" % print_string)


    return render_template('marked_as_read.html', entry_ids=result, feed_id=request.form['feed_id'], current_page=request.form['current_page'])