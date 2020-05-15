import os
from unidecode import unidecode
import mosaicbin.settings as settings
from threading import Thread
from queue import Queue

from skimage.io import imread, imshow
from skimage.transform import resize
from skimage.util import img_as_ubyte
from PIL import Image, ImageFile
import time
import random # for image name randomization
import string # for image name randomization

track_thread_status = {}


def clean_entries(entries):
    import dateutil.parser
    from bs4 import BeautifulSoup as BS

    print("len(entries): %s" % len(entries))
    for e in entries:
        for k in e:
            print("key: %s\nvalue: %s" % (k, e[k]))

        # make date readable
        try:
            x = dateutil.parser.parse(e['published'])
            e['published_human_readable'] = x.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception as e:
            print(e)
            print("Date not in correct format. Setting to 1970-01-01 00:00:00.")
            e['published_human_readable'] = "1970-01-01 00:00:00 UTC"

        try:
            # process the html
            print("e['content']: %s" % e['content'])

            # if the content is blank but everything else is good
            # A NoneType will mess up later, so let's just make it a string now
            if e['content'] is None:
                e['content'] = str("Mosaicbin: no content.")

            else:
                soup = BS(e['content'], features="html.parser")

                #track_thread_status = {} # needed to verify that images are all converted before moving on
                # first, let's convert all images to jpegs and resize them

                # only go through the image conversion if there is at least one image
                image_count = len(soup.find_all('img')) # used later to prevent unnecessary waiting on threads
                if image_count < 1:
                    pass
                else:
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


                if settings.loband is True:
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

        except Exception as e:
            print(e)
            e['content'] = "Error parsing or dealing with content in post."


    # Let's make sure all threads are done converting before we return entries
    # this will not update and not work if one thread fails
    timer = 0
    all_done = False
    if image_count == 0:
        all_done = True # this is set above if no images are found in the content

    while all_done is False:
        for image in track_thread_status:
            if track_thread_status[image] is False:
                all_done = False
            else:
                all_done = True
        if timer >= 5:
            all_done = True
            print('Giving up; not waiting for the rest of the threads to finish.')
        time.sleep(1)
        timer += 1
        print("Thread checker sleeping...")
    print("All threads done converting! (Or we gave up.)")

    return entries


def convert_image_to_jpg_from_url(url):

    try:
        # prep path for output
        segments = url.rpartition('/')
        # 2020-05-14 generating a hash from the URL to prevent image name collisions (multiple original.jpeg for example)
        url_hash = str(abs(hash(url)) % (10 ** 6)) # truncated to first 6 digits, unique enough
        filename = url_hash + segments[-1].split('?')[0] # removed the stuff after ? with whatever.jpg?w=557
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

    except Exception as e:
        print(e)
        return "mosaicbin/static/placeholder.gif"

def threaded_convert(url, output_filepath):
    
    print("url from convert_image_to_jpg_from_url: %s" % url)
    #url = "https://prasadpamidi.github.io/images/image2.jpg"

    try:
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

    except Exception as e:
        print(e)

    return True
