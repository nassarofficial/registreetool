import sys
import os
from queue import PriorityQueue
from urllib.request import urlopen
import json
import math
from io import StringIO 
from PIL import Image
from queue import PriorityQueue
import xml.etree.ElementTree as ET
import base64
import zlib
import struct
import time
import csv
import datetime
import pdb
import pickle

EARTH_RADIUS = 6371000
GOOGLE_CAR_CAMERA_HEIGHT = 3
def get_pano_lat_lng(pano, method=None):
	if 'CalibratedLocation' in pano:
		return (float(pano['CalibratedLocation']['lat']),
				float(pano['CalibratedLocation']['lng']))
	if method is None:
		method = 'original'
	if method == 'normal':
		return (float(pano['Location']['lat']), float(pano['Location'
				]['lng']))
	elif method == 'original':
		return (float(pano['Location']['original_lat']),
				float(pano['Location']['original_lng']))
	elif method == 'average':
		return ((float(pano['Location']['lat']) + float(pano['Location'
				]['original_lat'])) / 2.0, (float(pano['Location']['lng'
				]) + float(pano['Location']['original_lng'])) / 2.0)


def haversine_distance(
	lat1,
	lon1,
	lat2,
	lon2,
	):
	a = math.sin(math.radians((lat2 - lat1) / 2.0)) ** 2 \
		+ math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) \
		* math.sin(math.radians((lon2 - lon1) / 2.0)) ** 2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	return EARTH_RADIUS * c


def get_nearest_pano(
	latitude,
	longitude,
	radius,
	rank='closest',
	key=None,
	get_depth_map=False,
	get_pano_map=False,
	panos=None,
	method=None,
	return_pid=False,
	):
	if panos is None:  # Query google for the nearest pano
		url = \
			'https://cbks0.googleapis.com/cbk?output=json&oe=utf-8&it=all&dm=' \
			+ str(int(get_depth_map)) + '&pm=' + str(int(get_pano_map)) \
			+ '&rank=' + str(rank) + '&ll=' + str(latitude) + ',' \
			+ str(longitude) + '&radius=' + str(radius) \
			+ '&cb_client=apiv3&v=4&hl=en-US&gl=US'
		if not key is None:
			url = url + '&key=' + key
		response = urlopen(url)
		data = response.read()
		pano = json.loads(data.decode('utf-8'))
		if not return_pid:
			return pano
		else:
			if pano:
				return (pano, pano['Location']['panoId'])
			else:
				return ({}, {})


def crawl_all_panos(
	latitude,
	longitude,
	radius,
	rank='closest',
	seed_panos={},
	key=None,
	get_depth_map=False,
	get_pano_map=False,
	):
	seed_panos={}
	panos = seed_panos  # Typically seed_panos could contain just one panorama returned by get_nearest_pano(latitude, longitude)
	queue = PriorityQueue()
	pano_ls = []

	for pid in seed_panos.keys():
		pano = seed_panos[pid]
		(lat, lng) = get_pano_lat_lng(pano)
		dist = haversine_distance(latitude, longitude, lat, lng)
		if dist < radius:
			if 'Links' in pano:  # The google pano data structure contains links to the two neighboring panos on the same street.  Add these to the queue
				for l in pano['Links']:
					if not l['panoId'] in panos:
						panos[l['panoId']] = 'queued'
						queue.put((dist, l['panoId']))
	pano = get_nearest_pano(latitude, longitude, radius=radius,
							rank=rank)
	if pano is None or not 'Location' in pano:
		return panos
	queue.put((0, pano['Location']['panoId']))
	panos[pano['Location']['panoId']] = pano
	counter = 0
	while not queue.empty() and counter < 10:

		panoid = queue.get()[1]
		url = \
			'https://cbks0.googleapis.com/cbk?output=json&oe=utf-8&panoid=' \
			+ panoid + '&dm=' + str(int(get_depth_map)) + '&pm=' \
			+ str(int(get_pano_map)) \
			+ '&cb_client=apiv3&v=4&hl=en-US&gl=US'
		if not key is None:
			url = url + '&key=' + key
		response = urlopen(url)
		data = response.read()
		pano = json.loads(data.decode('utf-8'))
		counter = counter + 1
		if 'Location' in pano and pano['Location']['panoId'] == panoid:
			panos[pano['Location']['panoId']] = pano
			(lat, lng) = get_pano_lat_lng(pano)
			dist = haversine_distance(latitude, longitude, lat, lng)
			if dist < radius and 'Links' in pano:  # The google pano data structure contains links totwo neighboring panos on the same street.  Add to the queue

		# print("Adding " + pano['Location']['panoId'] + ' (' + str(lat) + ', ' + str(lng) + ') at distance ' + str(dist))

				pano_ls.append({
					'pano': pano,
					'lat': latitude,
					'lng': longitude,
					'dist': dist,
					})
				for l in pano['Links']:
					if not l['panoId'] in panos:
						panos[l['panoId']] = 'queued'
						queue.put((dist, l['panoId']))
		else:
			print('Error getting pano meta data ' + panoid)

	pano_ls = sorted(pano_ls, key=lambda item: item['dist'])
	pano_ls = pano_ls[0:4]

	for pano in pano_ls:
		# (x1, y1, x2, y2) = world_coordinates_to_streetview_pixel(pano['pano'], float(pano['lat']), float(pano['lng']))
		(x, y) = world_coordinates_to_streetview_pixel(pano['pano'], float(latitude), float(longitude))
		pano['x'] = x
		pano['y'] = y
		# pano['y1'] = y1
		# pano['y2'] = x2
	seed_panos={}

	return pano_ls


def world_coordinates_to_streetview_pixel(
	pano,
	lat,
	lng,
	height=0,
	zoom=None,
	object_dims=None,
	method=None,
	):
	camera_height = GOOGLE_CAR_CAMERA_HEIGHT  # ballpark estimate of the number of meters that camera is off the ground
	max_zoom = int(pano['Location']['zoomLevels'])
	pitch = 0  # float(pano['Projection']['tilt_pitch_deg'])*math.pi/180
	yaw = float((pano['Projection']['calibrated_pano_yaw_deg'
				] if 'calibrated_pano_yaw_deg' in pano['Projection'
				] else pano['Projection']['pano_yaw_deg'])) * math.pi \
		/ 180
	(lat1, lng1) = get_pano_lat_lng(pano, method=method)

	(dx, dy) = (math.cos(math.radians(lat1))
				* math.sin(math.radians(lng - lng1)),
				math.sin(math.radians(lat - lat1)))
	look_at_angle = math.pi + math.atan2(dx, dy) - yaw
	while look_at_angle > 2 * math.pi:
		look_at_angle = look_at_angle - 2 * math.pi
	while look_at_angle < 0:
		look_at_angle = look_at_angle + 2 * math.pi
	z = math.sqrt(dx * dx + dy * dy) * EARTH_RADIUS

	if zoom is None:  # default to highest resolution image
		zoom = max_zoom
	down = int(math.pow(2, max_zoom - zoom))  # downsample amount
	(image_width, image_height) = (int(pano['Data']['image_width'])
								   / down, int(pano['Data'
								   ]['image_height']) / down)

	x = image_width * look_at_angle / (2 * math.pi)
	y = image_height / 2 - image_height * (math.atan2(height
			- camera_height, z) - pitch) / math.pi
	return (x, y)

def create_single_annot(name, obj,maintree,loc):
    s = """<annotation>
        <filename>""" + name \
                    + """.jpg</filename>
        <source>
                <annotation>Pasadena Aerial View</annotation>
                <database>Pasadena Tree Database</database>
                <image>google</image>
        </source>
        <object>
                <name>tree</name>
                <bndbox>
                        <xmax>"""+str(int(round(obj['x2']/8)))+"""</xmax>
                        <xmin>"""+str(int(round(obj['x1']/8)))+"""</xmin>
                        <ymax>"""+str(int(round(obj['y2']/8)))+"""</ymax>
                        <ymin>"""+str(int(round(obj['y1']/8)))+"""</ymin>
                </bndbox>
                <pose>Unspecified</pose>
                <truncated>0</truncated>
                <difficult>0</difficult>
        </object><segmented>0</segmented>
        <target>"""+str(maintree)+"""</target>
        <location>"""+str(loc[0])+","+str(loc[1])+"""</location>

        <size>
                <depth>3</depth>
                <height>"""+str(2048)+"""</height>
                <width>"""+str(1024)+"""</width>
        </size>
</annotation>"""
    return s

def create_multi_annot(name, obj, maintree,loc):
    o= ""
    s = """<annotation>
        <filename>""" + name \
                    + """.jpg</filename>
        <size>
                <depth>3</depth>
                <height>"""+str(2048)+"""</height>
                <width>"""+str(1024)+"""</width>
        </size>
        <source>
                <annotation>Pasadena Aerial View</annotation>
                <database>Pasadena Tree Database</database>
                <image>google</image>
        </source>"""
    for i in range(len(obj)):
        o= o + """<object>
                <name>tree</name>
                <bndbox>
                        <xmax>"""+str(int(round(obj[i]['x2']/8)))+"""</xmax>
                        <xmin>"""+str(int(round(obj[i]['x1']/8)))+"""</xmin>
                        <ymax>"""+str(int(round(obj[i]['y2']/8)))+"""</ymax>
                        <ymin>"""+str(int(round(obj[i]['y1']/8)))+"""</ymin>
                </bndbox>
                <pose>Unspecified</pose>
                <truncated>0</truncated>
                <difficult>0</difficult>

        </object>"""

    t = """<segmented>0</segmented><target>"""+str(maintree)+"""</target>
            <location>"""+str(loc[0])+","+str(loc[1])+"""</location>

</annotation>"""
    return s+o+t

def download_full_pano_image(pano, zoom=None, key=None, api='javascript', out_dir=None, tiles=None, max_retries=0):
  max_zoom = int(pano['Location']['zoomLevels'])
  if zoom is None: zoom = max_zoom  # default to highest resolution image
  down = int(math.pow(2,max_zoom-zoom))  # downsample amount
  image_width, image_height = int(pano['Data']['image_width'])/down, int(pano['Data']['image_height'])/down
  tile_width, tile_height = int(pano['Data']['tile_width']), int(pano['Data']['tile_height'])
  full_pano_image = Image.new("RGB", (image_width, image_height), "black")
  num_x, num_y = int(math.ceil(image_width / float(tile_width))), int(math.ceil(image_height / float(tile_height)))
  if not out_dir is None: 
    full_name = out_dir + '/' + pano['Location']['panoId'] + '_z' + str(zoom) + '.jpg'
    if os.path.isfile(full_name):
      try:
        im = Image.open(full_name)
        return im
      except IOError:
        print("IOError reading image " + full_name + " in download_full_pano_image()")
        # os.rename(full_name, full_name + '.bad')
    # print 'Downloading ' + full_name
  for tile_y in range(num_y):
    for tile_x in range(num_x):
      download = tiles is None or tiles[tile_x,tile_y]
      tile = None
      if not out_dir is None and download: 
        fname = out_dir + '/' + pano['Location']['panoId'] + '_x' + str(tile_x) + '_y' + str(tile_y) + '_z' + str(zoom) + '.jpg'
        if os.path.isfile(fname):
          try:
            tile = Image.open(fname)
            download = False
          except IOError:
            # print "IOError reading image " + fname + " in download_full_pano_image()"
            os.rename(fname, fname + '.bad')
      if download:
        if api=='javascript':  # javascript api
          url = 'http://cbk0.google.com/cbk?output=tile&panoid='+pano['Location']['panoId']+'&zoom='+str(zoom)+'&x='+str(tile_x)+'&y='+str(tile_y)
        else:  # static street view api, doesn't work currently, not implemented correctly
          url = 'https://maps.googleapis.com/maps/api/streetview?size='+pano['Data']['tile_width']+'x'+pano['Data']['tile_height']+'&pano='+pano['Location']['panoId']+'&fov='+str(360.0/num_x)+'&heading='+str((tile_x+.5)*360.0/num_x)+'&pitch='+str((num_y/2.0-tile_y+.5)*180.0/num_y)
        if not key is None: url = url + '&key=' + key
        for num_retries in range(1+max_retries):
          try:
            response = urllib2.urlopen(url)
            data = response.read()
          except err:
            #print 'Error '+str(err.code)+' downloading image ' + url + ' ' + fname
            # print 'Error '+str(err.code)+' downloading pano ' + url + ' ' + str(pano['Location']['panoId'])
            if err.code == 400:
              # print 'aborting ' + url + ' ' + fname
              open(fname+'.bad', 'a').close()
              return None
            if num_retries < max_retries:
              time.sleep(math.pow(2, num_retries+1))
              continue
          except:
            # print 'Unknown Error downloading image ' + url + ' ' + fname
            if num_retries < max_retries:
              time.sleep(math.pow(2, num_retries+1))
              continue
        try:
          tile = Image.open(StringIO(data))
        except:
          # print "IOError reading image " + fname + " in download_full_pano_image()"
          return None
      if not tile is None:
        full_pano_image.paste(tile, (tile_x*tile_width, tile_y*tile_height))
  return full_pano_image
