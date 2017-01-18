import re
import json

f = open('input.txt', 'r')
lines = f.readlines()
# print data

g = open('output.txt', 'w')
gpx = open('favourites.gpx', 'wt')
header = """
<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<gpx version="1.1" creator="OsmAnd+" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
"""
print >> gpx, header


kml = open('swimming_holes.kml', 'wt')
kml_header = """
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
  <Style id="placemark-blue">
    <IconStyle>
      <Icon>
        <href>http://mapswith.me/placemarks/placemark-blue.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-brown">
    <IconStyle>
      <Icon>
        <href>http://mapswith.me/placemarks/placemark-brown.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-green">
    <IconStyle>
      <Icon>
        <href>http://mapswith.me/placemarks/placemark-green.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-orange">
    <IconStyle>
      <Icon>
        <href>http://mapswith.me/placemarks/placemark-orange.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-pink">
    <IconStyle>
      <Icon>
        <href>http://mapswith.me/placemarks/placemark-pink.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-purple">
    <IconStyle>
      <Icon>
        <href>http://mapswith.me/placemarks/placemark-purple.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-red">
    <IconStyle>
      <Icon>
        <href>http://mapswith.me/placemarks/placemark-red.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-yellow">
    <IconStyle>
      <Icon>
        <href>http://mapswith.me/placemarks/placemark-yellow.png</href>
      </Icon>
    </IconStyle>
  </Style>
 """
print >> kml, kml_header
print >> kml, """
    <name>Swimming Holes</name>
    <visibility>1</visibility>
"""

all_points = []

for line in lines:
    results = re.findall('lat=([ 0-9\.]+),\s+lon=([0-9\.-]+)', line)
    if len(results) > 0:
        data = {}
        names = re.findall('^([A-Z ]+\[[A-Z ]+\]):', line)
        assert len(names) <= 1
        name = 'Unknown'
        if len(names) == 1: name = names[0]
        for lat, lon in results:
            print >>g, "{}, {}, {}".format(lat, lon, name)
        data['lat'] = lat
        data['lon'] = lon
        data['name'] = name
        all_points.append(data)
        # print results, name

        print >> gpx, '  <wpt lat="{}" lon="{}">'.format(lat, lon)
        print >> gpx, '    <name>{}</name>'.format(name)
        print >> gpx, '    <type>Swimming holes</type>'
        print >> gpx, """
            <extensions>
              <color>#b410c0f0</color>
            </extensions>"""
        print >> gpx, '  </wpt>'

        print >> kml, """
          <Placemark>
            <name>{name}</name>
            <TimeStamp><when>2015-08-15T15:17:13Z</when></TimeStamp>
            <styleUrl>#placemark-red</styleUrl>
            <Point><coordinates>{lon},{lat}</coordinates></Point>
            <ExtendedData xmlns:mwm="http://mapswith.me">
              <mwm:scale>15</mwm:scale>
            </ExtendedData>
          </Placemark>
        """.format(name=name, lat=lat, lon=lon)


print >> gpx, '</gpx>'
gpx.close()

print >> kml, """
</Document>
</kml>
"""
kml.close()

# results = re.findall('lat=([ 0-9\.]+),\s+lon=([0-9\.-]+)', data)
# print results
# print len(results)

g.close()

pts = open('points.json', 'wt')
json.dump(all_points, pts, indent=4)
pts.close()
# for lat, lon in results:
#     print >>g, "{}, {}"
