import requests
import datetime
import os
from unidecode import unidecode
import mosaicbin.settings as settings
from threading import Thread
from queue import Queue

from skimage.io import imread, imshow
from skimage.transform import resize
from skimage.util import img_as_ubyte
from PIL import Image, ImageFile

endpoint = "https://api.feedbin.com/v2/"
try:
    creds = (str(os.environ['FEEDBIN_USERNAME']), str(os.environ['FEEDBIN_PASSWORD']))
except:
    print("Credentials not available. Run:\nexport FEEDBIN_USERNAME='whatever'\nexport FEEDBIN_PASSWORD='whatever'\n")
#creds = ('username@domain.net', 'password')
verbose = False

global track_thread_status
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

    subs_dict = get_subs_dict()
    # for x in subs_dict:
    #     print("%s %s" % (x, subs_dict[x]))


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
        pass

    return r.json()


def get_subs_dict():

    path = "subscriptions.json"
    url = "%s%s" % (endpoint, path)
    if verbose:
        print(url)

    r = requests.get(url, auth=creds)

    subs_dict = {}

    for i in r.json():
        if verbose:
            print(i)
        subs_dict[i['feed_id']] = i['title']

    return subs_dict


def get_all_unread_entries():

    path = "unread_entries.json"
    url = "%s%s" % (endpoint, path)
    if verbose:
        print(url)

    r = requests.get(url, auth=creds)

    return r.json()

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
    if len(r.json()) > 0:
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

def clean_entries(entries):
    import dateutil.parser
    from bs4 import BeautifulSoup as BS

    for e in entries:
        for k in e:
            print("key: %s\nvalue: %s" % (k, e[k]))

        # make date readable
        x = dateutil.parser.parse(e['published'])
        e['published_human_readable'] = x.strftime("%Y-%m-%d %H:%M:%S UTC")

        # process the html
        soup = BS(e['content'], features="html.parser")

        #track_thread_status = {} # needed to verify that images are all converted before moving on
        # first, let's convert all images to jpegs and resize them
        for img in soup.find_all('img'):

            # now, let's remove the size attribute from images
            del(img['srcset'])
            #print("after srcset removal: %s" % img)

            #new_url, width = convert_image_to_jpg_from_url(img['src'])


            track_thread_status[img['src']] = False # sets the image status since it's not done yet

            #### for testing threading and ensuring page doesn't load before all threads are done
            print("*****track_thread_status:*****" % track_thread_status)
            for i in track_thread_status:
                print(track_thread_status[i])
            print("**********")

            new_url = convert_image_to_jpg_from_url(img['src']) # removed width

            # new_tag = soup.new_tag('img', src=new_url, width=width)
            new_tag = soup.new_tag('img', src=new_url) # removed width, but put it back if things break
            print("after: %s" % new_url)

            # this is confusing to me
            # originally had img = new_tag, which looked like it worked but then didn't
            # this prints out img incorrectly but works in practice
            # look into why this is later
            img.replaceWith(new_tag)
            print("final img: %s\n----" % img)

            #### for testing threading and ensuring page doesn't load before all threads are done
            print("*****track_thread_status:*****" % track_thread_status)
            for i in track_thread_status:
                print(track_thread_status[i])
            print("**********")

        if settings.loband == True:
            for link in soup.find_all('a'):
                print("##%s" % link)
                loband_url = link['href']
                loband_url = loband_url.replace("http://", "")
                loband_url = loband_url.replace("https://", "")
                loband_url = "http://www.loband.org/loband/filter/" + '/'.join(loband_url.split('/')[0].split('.')[::-1]) + '/%20/' + '/'.join(loband_url.split('/')[1:])
                print("######%s" % loband_url)
                link['href'] = loband_url
                print("###%s" % link)

        # delete iframes completely
        for iframe in soup('iframe'):
            iframe.extract()

        # delete svg completely
        for svg in soup('svg'):
            svg.extract()

        e['content'] = str(soup)

        # lossy conversion to 7-bit ascii (helps with curly quotes, etc)
        e['content'] = unidecode(e['content'])
        e['title'] = unidecode(e['title'])

    return entries

def convert_image_to_jpg_from_url(url):

    # prep path for output
    segments = url.rpartition('/')
    filename = segments[-1].split('?')[0] # removed the stuff after ? with whatever.jpg?w=557
    output_filepath = "mosaicbin/static/generated/%s" % filename
    static_path = "/static/generated/"

    if os.path.exists(output_filepath):
        print("File exists, so just getting it's width and returning the path and width.")
        img1 = imread(output_filepath)
        width = img1.shape[1]
        new_url = static_path + filename
        track_thread_status[url] = True

        return new_url # , width

    else:
        print("File doesn't exist, so let's create it...")
        track_thread_status[url] = threaded_convert(url, output_filepath)
        worker = Thread(target=threaded_convert, args=(url, output_filepath,))
        worker.setDaemon(True)
        worker.start()

        new_url = "%s" % static_path + filename
        print("new url from function: %s" % new_url)

        return new_url# , # width not returning width anymore for parallelization

def threaded_convert(url, output_filepath):
    
    print("url from convert_image_to_jpg_from_url: %s" % url)
    #url = "https://prasadpamidi.github.io/images/image2.jpg"
    img1 = imread(url)

    height = img1.shape[0]
    width = img1.shape[1]
    max_output_width = settings.img_width # base setting for how wide these images will be
    print("height: %s  width: %s" % (height, width))

    if width >= max_output_width:
        print("width >= %s, resizing..." % settings.img_width)
        ratio = height/width # for fixed width images
        output_height = int(max_output_width * ratio) # figure out how wide the output image will be
        img1 = resize(img1, (output_height, max_output_width))
        print("ratio: %s output_height: %s  max_output_width: %s" % (ratio, output_height, max_output_width))
        width = max_output_width # so I can pass the correct width out of this function

    # convert
    img3 = img_as_ubyte(img1)
    img4 = Image.fromarray(img3)
    img5 = img4.convert("RGB") # if the source has alpha, remove it

    # save the file and generate the new url
    img5.save(output_filepath, "JPEG", quality=80, optimize=True, progressive=True)

    return True

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
