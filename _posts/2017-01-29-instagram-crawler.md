---
layout: post
title:  "Writing Instagram crawler"
---

This note is about small instagram crawler.
I used it to download photos and their metadata
for a project of visualizing photos from my roadtrip
(see [Arizona Trip 2016](/projects/arizona) page).

## Introduction

Instagram doesn't provide API to access your own photos, so we have to download
html pages and parse it manually.

The data we need to obtain about photos:

* id
* display image
* thumbnail image
* location (lat + lon)

Let's write some code to achieve the goal.

## 1. Get html data from profile page

Okay, we have instagram profile page open in browser, how do we get data shown to us?

First thing I tried was to use `View Page Source` menu option.
There was nice json with information about photos:

```html
<script type="text/javascript">window._sharedData = ...
</script>
```

But it only contained data for first 12 photos to it wasn't useful to get all of them.
The actual data is hidden in `react-root` span, but it's empty in the page source:

```html
<body class="">
<span id="react-root"></span>
```

What we can do instead, is to `Inspect` the actual DOM in browser debugger and then
`Copy > Copy outerHTML` for `<body>` tag.

It can probably be automated further, but this is really one-off operation that
doesn't take much time.

**NOTE**: this method will give only visible photos, so we need to scroll until all desired
photos are shown.


## 2. Extract photo ids

Now we have giant html dump from which we somehow need to extract relevant to us
information. I found XPath-based approach to be pretty nice. And of course python
already has a library for that.

Let's do `Inspect > Copy > Copy XPath` on two of the photos:

```python
//*[@id="react-root"]/section/main/article/div/div[1]/div[49]/a[1]
//*[@id="react-root"]/section/main/article/div/div[1]/div[50]/a[2]
```

The difference is only in the last 2 parts. Basically `div[X]` specifies row `X`,
while `a[Y]` specifies column `Y`.

Then we can run xpath query on downloaded html:

```python
import lxml

s = open(HTML_FILE).read()
tree = lxml.html.fromstring(s)

selector = \
'//*[@id="react-root"]/section/main/article/div/div[1]/div[*]/a[*]'
elems = tree.xpath(selector)
```

This will give us a list of all photos which we can iterate over and extract
`photo_id` and `thumbnail` url. Instances of class `lxml.html.HtmlElement` has
a field `attrib` that contains all properties of html tag. Let's use that to get
the data:

```python
# elem == <a class="_8mlbc _vbtk2 _t5r8b" href="/p/BNiq9hsBXo3/?taken-by=pankdm">
tag = elem.attrib['href']
# tag == '/p/BOtc42gAaGL/?taken-by=pankdm'
photo_id = tag.split('/')[2]

img_html = elem.xpath('div/div[1]/img')
thumbnail_src = img_html[0].attrib['src']
```

## 3. Extract location

Next thing we need to do is to obtain geo coordinates of the photos:

```
photo_id -> location_id -> (lat, lon)
```

We need to download html programmatically. Python library `requests` is a good fit:

```python
import requests

r = requests.get('http://instagram.com/p/{}'.format(photo_id))
print r.text
```

For such pages `window._sharedData` in javascript contains enough data to extract what we want,
so we can parse that using regular expressions:

```python
import re
import json

def fetch_json(url):
    r = requests.get('url')
    match = re.search('window._sharedData = (.*);</script>', r.text)
    return json.loads(match.group(1))
```

Combining this all together:

```python
d = fetch_json('http://instagram.com/p/{}'.format(photo_id))
node = d['entry_data']['PostPage'][0]['media']
location_id = node['location']['id']
display_src = node['display_src']

d = fetch_json('http://instagram.com/explore/locations/{}'.format(location_id))
node = d['entry_data']['LocationsPage'][0]['location']
lat = node['lat']
lon = node['lon']
```

## 4. Download photos

The only thing left is to download the actual photo files (both thumbnail and full size).
We can use `requests` library to get the job done:

```python
def download_photo(url, path):
    r = requests.get(url)
    f = open(path, 'wb')
    f.write(r.content)
    f.close()

download_photo(display_src, 'data/{}.jpg'.format(photo_id))
download_photo(thumbnail_src, 'data/th_{}.jpg'.format(photo_id))
```
