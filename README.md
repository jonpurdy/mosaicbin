#  Mosaicbin ![Mosaicbin logo](https://raw.githubusercontent.com/jonpurdy/mosaicbin/master/mosaicbin/static/icon64.gif)

Mosaicbin is a client and proxy for Feedbin, which is a web-based RSS service. Mosaicbin enables old computers and old browsers to read RSS feeds despite not having any modern SSL or standards support. It does this by proxying feeds and entries from the Feedbin API, formatting them and converting images to be smaller and legacy-compatible, and serving up the result as regular non-SSL HTML 3.2(ish).

## Prerequisites

Mac OS X or Linux
Python 3.x
PIP
pipenv (optional)

## Installation

After installing the prerequisites:

    git clone https://github.com/jonpurdy/mosaicbin.git
    cd mosaicbin
    pip install requirements.txt

I haven't figured out the best way to deal with user credentials yet. But for now, just set them as environment variables:

	export FEEDBIN_USERNAME='your_feedbin_username'
	export FEEDBIN_PASSWORD='your_feedbin_password'

I've written a helper script to get you started:

	./start.sh

This will open up the default Flask webserver on port 5000. You can connect to localhost:5000 on the machine you are serving from to test, or to the IP address if your machine if connecting from a legacy computer.

## Testing

Tests are done with PyTest. Just run `pytest`. Coverage is basic and incomplete but should be enough to deal with any future maintenance.

## To Do

* ✓ use templates
* ✕ use api key instead of password (not possible, HTTP Basic only and no API keys)
* ✓ pagination on entries
* ✓ put credentials in env variable
* ✓ image conversion to non-http jpeg
	* ✓ intercept post, grab images, process and serve them for low bandwidth
	* ✓ parallelize image conversion
	* ✓ check if image has already been converted
	* ✕ clean up conversion directory automatically (will worry about this later)
	* ✓ easy way to change output size (in menu or config file)
* ✓ put unread counts next to feed titles (needs optimization)
* create vagrantfile
* ✓ get rights to hamburger logo
* ✓ create license
* ✓ config/settings file


## Links

Feedbin website: [feedbin.com](feedbin.com)  
License: [GPL v3](https://github.com/jonpurdy/mosaicbin/blob/master/LICENSE.txt)