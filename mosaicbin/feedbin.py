import requests
import datetime
import os
import mosaicbin.settings as settings

endpoint = "https://api.feedbin.com/v2/"
try:
    creds = (str(os.environ['FEEDBIN_USERNAME']), str(os.environ['FEEDBIN_PASSWORD']))
except Exception as e:
    print("Credentials not available. Run:\nexport FEEDBIN_USERNAME='whatever'\nexport FEEDBIN_PASSWORD='whatever'\n")
#creds = ('username@domain.net', 'password')
verbose = True

track_thread_status = {}

    # now, if a user clicks on the title of a feed, it will redirect them to the
    # unread entries of that feed

    # example using daringfireball
    # {'id': 274178, 'created_at': '2013-04-28T14:56:57.319654Z', 'feed_id': 47,
    # 'title': 'Daring Fireball', 'feed_url': 'http://daringfireball.net/index.xml',
    # 'site_url': 'https://daringfireball.net/'}


    # first, get all unread entries for all feeds
    # make a list of ids in unread_entry_ids


def get_subs_and_tags():

    tagging_response = get_tagging()
    if verbose:
        print(len(tagging_response))

    # first, build list of tags
    tag_name_list = []
    for t in tagging_response:
        # the code below helped ensure string comparison was working
        # my_str_as_bytes = str.encode(t['name'])
        # my_decoded_str = my_str_as_bytes.decode()
        # print("before:%s bytes:%s after: %s" % (t['name'], my_str_as_bytes, my_decoded_str))
        if t['name'] in tag_name_list:
            #print("in")
            pass
        else:
            tag_name_list.append(t['name'])
            #print("out, adding")
        #print(tag_name_list)
    if verbose:
        print("tag_name_list: %s" % tag_name_list)

    # next, create dictionary out of the tag_name_list
    tags = {}
    for t in tag_name_list:
        tags[t] = []
    if verbose:
        print(tags)

    # # now, interate through tagging_response and add feed_id to the dictionary
    for i in tagging_response:
        tags[i['name']].append(i['feed_id'])

    # let's verify we have what we need
    feed_count = 0
    for x in tags:
        if verbose:
            print("%s %s %s" % (x, tags[x], len(tags[x])))
        feed_count += len(tags[x])
    if verbose:
        print("feed_count = %s" % feed_count)

    
    # now that we have that dictionary with each tag and a list of feeds for each tag,
    # let's get each feed_id's name through subscriptions.json
    # once we do this, we can print a list of names
    # if the user clicks a name, it links to a page with unread entries for that feed



    subs_dict, feeds_dict = get_subs_dict()

    for f in feeds_dict:

        feeds_dict[f].unread_count = get_unread_entry_count_of_feed(feeds_dict[f].feed_id)

        print(feeds_dict[f].feed_id)
        print(feeds_dict[f].title)
        print(feeds_dict[f].unread_count)


    return subs_dict, tags


def get_tagging():

    path = "taggings.json"
    url = "%s%s" % (endpoint, path)
    if verbose:
        print(url)

    print(creds)
    r = requests.get(url, auth=creds)
    if verbose:
        print(r)
    for i in r.json():
        if verbose:
            print(i)

    return r.json()


def get_subs_dict():

    path = "subscriptions.json"
    url = "%s%s" % (endpoint, path)
    if verbose:
        print(url)

    r = requests.get(url, auth=creds)

    subs_dict = {}
    feeds_dict = {} # new hotness

    for i in r.json():
        if verbose:
            print(i)
        subs_dict[i['feed_id']] = i['title']
        feeds_dict[i['feed_id']] = Feed(title=i['title'], feed_id=i['feed_id'], unread_count=0)

    # for x in subs_dict:
    #     print("%s %s" % (x, subs_dict[x]))


    return subs_dict, feeds_dict


def get_all_unread_entries():

    path = "unread_entries.json"
    url = "%s%s" % (endpoint, path)
    if verbose:
        print(url)

    r = requests.get(url, auth=creds)

    return r.json()

def get_unread_entries_of_feed(feed_id):
    """ Returns a list of unread entries for a particular feed.
    """

    unread_entries_all = get_all_unread_entries()
    unread_entries_feed = []

    one_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
    path = "feeds/%s/entries.json" % feed_id # no need for since anymore 
    url = "%s%s" % (endpoint, path)
    r = requests.get(url, auth=creds)

    if r.json(): # if there are entries in this feed
        for entry in r.json(): 
            if entry['id'] in unread_entries_all:
                #print("this entry_id %s is unread" % entry['id'])                
                unread_entries_feed.append(entry)

    return unread_entries_feed

def get_unread_entry_count_of_feed(feed_id):
    """ Returns an int of the count of unread entries for a particular feed.
    """ 
    unread_count = len(get_unread_entries_of_feed(feed_id))
    #unread_count = 0

    return unread_count

def get_entries(feed_id, unread, per_page, page_no):

    # note that using per_page is irrelevant, it may return 5 from the API
    # but if only 2 are unread then it'll just return two
    # need to use another function to group entries after being gotten

    one_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
    # ?since=2013-02-02T14:07:33.000000Z
    # since = "?since=%sZ" % one_year_ago.isoformat()

    #path = "feeds/%s/entries.json%s&per_page=%s&page=%s" % (feed_id, since, per_page, page_no)
    #path = "feeds/%s/entries.json%s" % (feed_id, since)
    path = "feeds/%s/entries.json" % feed_id # no need for since anymore 
    url = "%s%s" % (endpoint, path)
    print("URL HERE: %s" % url)

    r = requests.get(url, auth=creds)

    unread_entries_of_this_feed = []
    these_entries = [] # for storing 

    # this might need fixing
    print("len(r.json()): %s" % len(r.json()))
    # if len(r.json()) > 0: # delete this later if no issues
    if r.json():
        print("let's start the loop: all of feed_id %s's entries len(r.json()) is greater than 0" % feed_id)
        for entry in r.json(): 
            if entry['id'] in unread:
                #print("this entry_id %s is unread" % entry['id'])                
                unread_entries_of_this_feed.append(entry)

        print("ongoing unread entries list get_Entries() length is len(entries): %s " % len(unread_entries_of_this_feed))
        print("Done creating the unread entries list. Let's move on...")


        print("We need to return the correct number (per_page) of unread entries, starting on the correct entry paginated (page_no).")

        # calculation for start_point
        # page_no     1   2   3   1   2   3   1   2   3
        # per_page    2   2   2   5   5   5   4   4   4
        # start_entry 1   3   5   1   6   11  1   5   9

        start_point = (per_page * page_no) - (per_page - 1) - 1 # final -1 is for 0-based index of r.json()
        i = 0

        print("start_point: %s  | per_page: %s | page_no: %s | entries: %s" % (start_point, per_page, page_no, len(unread_entries_of_this_feed)))

        # two conditions required
        # 1. len(these_entries) must be less than per_page 
        # 2. len(these_entries) must be less than total of this feed's unread entries
        # so, we'll just set per_page to the length of feed's unread
        # a bit hacky, but it works ()
        if len(unread_entries_of_this_feed) < per_page:

            # handle if requesting a page other than the first, and
            # less than that number of entries
            if page_no > 1:
                 return these_entries, 0
            per_page= len(unread_entries_of_this_feed)

        while len(these_entries) < per_page:
            print("i: %s" % i)
            print("len(these_entries): %s  len(unread_entries_of_this_feed): %s" % (len(these_entries), len(unread_entries_of_this_feed)))
            if i >= start_point:
                entry = unread_entries_of_this_feed[i]
                print(unread_entries_of_this_feed[i]['id'])               
                these_entries.append(entry)
            i += 1
            print("len(these_entries): %s\n------" % len(these_entries))

            
        return these_entries, len(r.json())

    else:
        return these_entries, 0


def mark_entries_as_read(entry_ids):

    path = "unread_entries/delete.json"
    url = "%s%s" % (endpoint, path)
    if verbose:
        print(url)

    print("received %s" % entry_ids)

    #url = "https://httpbin.org/post" # comment this to actually mark as unread

    # hack to get around feedbin api not accepting multiple entry IDs
    # r = requests.post(url, auth=creds, data = {'unread_entries':entry_ids})
    # print("r.text: %s" % r.text)

    # return r.text

    feedbin_result = []
    for i in entry_ids:
        r = requests.post(url, auth=creds, data = {'unread_entries':i})
        print("r.text: %s" % r.text)
        feedbin_result.append(r.text)

    return feedbin_result

    
    #return 0

class Feed(object):
    """ A Feedbin feed
    """
    title = ""
    feed_id = ""
    unread_count = ""

    def __init__(self, title, feed_id, unread_count):
        self.title = title
        self.feed_id = feed_id
        self.unread_count = unread_count


