import xml.etree.ElementTree as et
import sys
import re

def codes_to_coords(a, b, c):
    a = int(a)
    b = int(b)
    c = int(c)
    if (a % 1000 - a % 100) / 100 == 1:
        lat_sign = 1
        lon_sign = 1
    elif (a % 1000 - a % 100) / 100 == 2:
	    lat_sign = -1
	    lon_sign = 1
    elif (a % 1000 - a % 100) / 100 == 3:
	    lat_sign = 1
	    lon_sign = -1
    elif (a % 1000 - a % 100) / 100 == 4:
	    lat_sign = -1
	    lon_sign = -1
    if ((c % 100000 - c % 10000) / 10000 + (c % 100 - c % 10) / 10) % 2 == 0:
	    lat = lat_sign * ( \
		(a % 10000 - a % 1000) / 100 \
		+ (b % 100 - b % 10) / 10 \
		+ (b % 100000 - b % 10000) / 100000 \
		+ (c % 1000 - c % 100) / 10000 \
		+ (a % 1000000 - a % 100000) / 100000000 \
		+ (c % 100 - c % 10) / 100000 \
		+ a % 10 * 1.0E-5)
    elif ((c % 100000 - c % 10000) / 10000 + (c % 100 - c % 10) / 10) % 2 != 0:
	    lat = lat_sign * ( \
		(b % 1000000 - b % 100000) / 10000 \
		+ a % 10 + (a % 10000 - a % 1000) / 10000 \
		+ (c % 1000000 - c % 100000) / 10000000 \
		+ (c % 1000 - c % 100) / 100000 \
		+ (c % 100 - c % 10) / 100000 \
		+ (a % 1000000 - a % 100000) / 10000000000)
    if ((c % 100000 - c % 10000) / 10000 + (c % 100 - c % 10) / 10) % 2 == 0:
	    lon = lon_sign * ( \
		(a % 100000 - a % 10000) / 100 \
		+ (c % 1000000 - c % 100000) / 10000 \
		+ c % 10 + (b % 1000 - b % 100) / 1000 \
		+ (b % 1000000 - b % 100000) / 10000000 \
		+ (a % 100 - a % 10) / 10000 \
		+ (c % 100000 - c % 10000) / 100000000 \
		+ b % 10 * 1.0E-5)
    elif ((c % 100000 - c % 10000) / 10000 + (c % 100 - c % 10) / 10) % 2 != 0:
	    lon = lon_sign * ( \
		(b % 100 - b % 10) * 10 \
		+ c % 10 * 10 \
		+ (a % 100 - a % 10) / 10 \
		+ (a % 100000 - a % 10000) / 100000 \
		+ (b % 1000 - b % 100) / 10000 \
		+ b % 10 * 0.001 \
		+ (c % 100000 - c % 10000) / 100000000 \
		+ (b % 100000 - b % 10000) / 1000000000)

    return lat, lon

gpx = sys.argv[1]

t = et.parse(gpx)
root = t.getroot()
xsi = root.tag[:-3]
groundspeak = '{http://www.groundspeak.com/cache/1/0/1}'
r = '[ >\n]\d{6}[ <\n]'

for child in root.findall(xsi+'wpt'):
    gccode = child.find(xsi+'name').text
    cache = child.find(groundspeak+'cache')
    gcname = cache.find(groundspeak+'name').text
    gctype = cache.find(groundspeak+'type').text
    if gctype == 'Wherigo Cache':
        description = cache.find(groundspeak+'short_description').text
        description += cache.find(groundspeak+'long_description').text
        dl = description.lower()
        if 'waldmeister' in dl or 'reverse' in dl or 'wherigo.com/cartridge/details.aspx?CGUID=dcdcd2ff-c171-4487-93bc-678f6d03ac4f' in dl:
            codes = re.findall(r, description)
            if len(codes) < 3:
                print('Listing for', gccode, 'does not seem to contain start code (' + str(gcname) + ')')
            else:
                for i, code in enumerate(codes):
                    codes[i] = ''.join(i for i in code if i.isdigit())
                lat, lon = codes_to_coords(codes[0], codes[1], codes[2])
                child.attrib['lat'] = str(lat)
                child.attrib['lon'] = str(lon)
                print(gccode, gcname, 'is at', lat, lon)
        #else:
        #    print(gccode, 'is probably not a reverse WIG (' + str(gcname) + ')' )

t.write(gpx)
