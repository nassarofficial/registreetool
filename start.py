#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, \
	jsonify, session  # For flask implementation
from pymongo import MongoClient  # Database connector
from bson.objectid import ObjectId  # For ObjectId to work
import json
from bson import Binary, Code
from bson import json_util
from bson.objectid import ObjectId
import os
import sys
from urllib.request import urlopen
import math
from queue import PriorityQueue

from random import randint, randrange
from datetime import datetime
from flask import Flask
from flask_bcrypt import Bcrypt
from funcs import *

EARTH_RADIUS = 6371000
GOOGLE_CAR_CAMERA_HEIGHT = 3
cl = \
	MongoClient('mongodb://user:password@server:39459/db'
				)
db = cl.db

app = Flask(__name__)
title = 'Multi Street View Annotation Tool'


###################################################################
##				Routes
###################################################################

@app.route('/home')
def home():
	return render_template('home.html', t=title, h='Home',userrole=session['role'])

@app.route('/hash')
def hash():
	passw = bcrypt.generate_password_hash("q2564")
	d = passw
	return d

@app.route('/logout')
def logout():
	session = None
	session = None
	return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
def index():

	db = cl.db
	error = None
	if request.method == 'POST':
		try:
			userret = db['users'].find({"user":request.form['username']})
			userret = list(userret)[0]

			if userret['user'] == request.form['username'] and bcrypt.check_password_hash(userret['pass'], request.form['password']) :
				session['user'] = request.form['username']
				session['role'] = userret['role']
				return redirect(url_for('home'))
			else:
				error = 'Invalid Credentials. Please try again.'
		except:
				error = 'Invalid Credentials. Please try again.'
		return render_template('index.html', t=title, h='Login',error=error)

	else:
		return render_template('index.html', t=title, h='Login',error=error)

@app.route('/GoBack')
def GoBack():
	select = session['dataset']
	cols = db[select].find()

	data = []
	for document in cols:
		tmp = str(document['_id'])
		del document['_id']
		document['_id'] = tmp
		data.append(document)
		break

	return render_template('LoadMarkers.html', t=title, h='Load Markers'
						   , data=data,center={"status":"None"})



@app.route('/ViewCreateDataset')
def viewcreatedataset():
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		return render_template('CreateDataset.html', t=title,
						   h='Create Dataset')

@app.route('/Settings')
def Settings():
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		#val for users
		col_select_users = 'users'
		col_users = db[col_select_users].find()
		# print(len(list(col_users)))
		u_val = len(list(col_users))

		#val for datasets
		datasets = db.collection_names()
		tbd = []
		for i in range(len(datasets)):
			if "_panos" in datasets[i]:
				tbd.append(datasets[i])
		for x in tbd:
			datasets.remove(x)
		datasets.remove('system.indexes')
		datasets.remove('users')
		try:
			datasets.remove('objectlabs-system')
			datasets.remove('objectlabs-system.admin.collections')
		except:
			pass

		# print(len(list(datasets)))

		d_val = len(list(datasets))

		return render_template('settings.html', t=title,
						   h='Settings', users_val=u_val, data_val= d_val)

@app.route('/SettingsDatasets')
def SettingsDatasets():
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		datasets = db.collection_names()
		tbd = []
		for i in range(len(datasets)):
			if "_panos" in datasets[i]:
				tbd.append(datasets[i])
		for x in tbd:
			datasets.remove(x)
		datasets.remove('system.indexes')
		datasets.remove('users')
		datasets.remove('classes')
		datasets.remove('settings')
		try:
			datasets.remove('objectlabs-system')
			datasets.remove('objectlabs-system.admin.collections')
		except:
			pass

		# print(len(list(datasets)))

		data = list(datasets)

		return render_template('settings_datasets.html', t=title,
						   h='Manage Datasets', data=data)

@app.route('/SettingsUsers')
def UsersDatasets():
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		cursor = db.users
		cursor = cursor.find({})
		dataset = list(cursor)
		data = []
		for x in dataset:
			data.append(x['user'])			

		print("_-_-_")
		print(data)
		return render_template('settings_users.html', t=title,
						   h='Manage Users', data=data)


@app.route('/CreateDataset', methods=['GET', 'POST'])
def CreateDataset():
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		select = request.form.get('datasetname')
		session['dataset'] = select
		db.create_collection(select)
		db.create_collection(select+"_panos")
		data = [{"location":{"coordinates":[8.534026, 47.380636]}}]
		return render_template('LoadMarkers.html', t=title,
							   h='Create Dataset',data=data,center={"status":"None"})

@app.route('/LoadMarkers')
def LoadMarkers():
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		cols = db.collection_names()
		tbd = []
		for i in range(len(cols)):
			if "_panos" in cols[i]:
				tbd.append(cols[i])
		for x in tbd:
			cols.remove(x)
		cols.remove('system.indexes')
		cols.remove('users')
		cols.remove('classes')

		try:
			cols.remove('objectlabs-system')
			cols.remove('objectlabs-system.admin.collections')
		except:
			pass
		return render_template('SelectMarkers.html', t=title,
							   h='Select Markers', data=cols)


@app.route('/LoadSelectedMarkers', methods=['GET', 'POST'])
def LoadSelectedMarkers():
        select = request.form.get('collections')
        cols = db[select].find()
        session['dataset'] = select

        data = []
        for document in cols:
                tmp = str(document['_id'])
                del document['_id']
                document['_id'] = tmp
                data.append(document)
                break

        return render_template('LoadMarkers.html', t=title, h='Load Markers'
                                                   , data=data, center={"status":"None"})

@app.route('/ContinueMarker', methods=['GET', 'POST'])
def ContinueMarker():
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		select = session['dataset']
		cols = db[select].find()
		lat = request.form.get('lat')
		lng = request.form.get('lng')
		center = {"lat":lat, "lng":lng}
		data = []
		for document in cols:
			tmp = str(document['_id'])
			del document['_id']
			document['_id'] = tmp
			data.append(document)
			break
		print(center)
		return render_template('LoadMarkers.html', t=title, h='Load Markers'
							  	, data=data, center=(center))


@app.route('/LoadAerialView', methods=['GET', 'POST'])
def LoadAerialView():
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		select = request.form.get('collections')
		cols = db[select].find()
		session['dataset'] = select

		data = []
		for document in cols:
			tmp = str(document['_id'])
			del document['_id']
			document['_id'] = tmp
			data.append(document)
			break
		return render_template('LoadMarkers.html', t=title, h='Load Markers'
							   , data=data, label=session['dataset'], center={"status":"None"})


@app.route('/Refresh')
def Refresh():
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		select = session['dataset']
		cols_pano = db[select+"_panos"]

		idd = session['idd']
		lat = session['lat']
		lng = session['lng']
		subid = idd
		data = crawl_all_panos(float(lat), float(lng), 100)
		payload = []
		for x in data:
			col = cols_pano.find_one({'_id': x['pano']['Location']['panoId']})
			if col != None:
				payload.append(col)
			else:
				payload.append({'_id':x['pano']['Location']['panoId'],"annotations":[],"pano_details":x['pano'], "x":x['x'], "y":x['y'],"lat":x['lat'],"lng":x['lng']})

		idd = [{"id":idd}]
		return render_template('AnnotateMarkers.html', data=payload, classes=classes, tree_id = idd,  t=title, h=subid)


@app.route('/AnnotateMarkers', methods=['GET', 'POST'])
def AnnotateMarkers():
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		select = session['dataset']
		cols_pano = db[select+"_panos"]

		idd = request.form.get('id')
		lat = request.form.get('lat')
		lng = request.form.get('lng')
		subid = request.form.get('id')
		session['idd'] = idd
		session['lat'] = lat
		session['lng'] = lng

		cols_trees =  db[select]
		col_tree = cols_trees.find_one({'_id': ObjectId(idd)})

		classes = db['classes'].find()
		classes = list(classes)
		del col_tree['_id']
		

		data = crawl_all_panos(float(lat), float(lng), 100)
		payload = []
		for x in data:
			col = cols_pano.find_one({'_id': x['pano']['Location']['panoId']})
			if col != None:
				payload.append(col)
			else:
				payload.append({'_id':x['pano']['Location']['panoId'],"annotations":[],"pano_details":x['pano'], "x":x['x'], "y":x['y'],"lat":x['lat'],"lng":x['lng']})

		idd = [{"id":idd}]
		return render_template('AnnotateMarkers.html', data=payload, tree_id = idd, classes=classes, tree = col_tree,  t=title, h=subid)



@app.route('/NextTree')
def NextTree():
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		select = session['dataset']
		cols = db[select]
		count = cols.count()
		array = list(cols.aggregate([{'$sample': {'size': 1 }}]))
		cols_pano = db[select+"_panos"]

		idd = array[0]['_id']
		iddob = str(array[0]['_id'])
		lat = array[0]['location']['coordinates'][1]
		lng = array[0]['location']['coordinates'][0]
		session['idd'] = iddob
		session['lat'] = lat
		session['lng'] = lng
		classes = db['classes'].find()
		classes = list(classes)

		cols_trees =  db[select]
		col_tree = cols_trees.find_one({'_id': ObjectId(idd)})
		del col_tree['_id']
		data = crawl_all_panos(float(lat), float(lng), 100)
		payload = []
		for x in data:
			col = cols_pano.find_one({ '$and' : [{'_id': x['pano']['Location']['panoId']},{ "annotated" : { "$exists" : False } }]})
			if col != None:
				payload.append(col)
			else:
				payload.append({'_id':x['pano']['Location']['panoId'],"annotations":[],"pano_details":x['pano'], "x":x['x'], "y":x['y'],"lat":x['lat'],"lng":x['lng']})

		idd = [{"id":iddob}]
		return render_template('AnnotateMarkers.html', data=payload, classes=classes, tree_id = idd, tree = col_tree, t=title, h=str(iddob))

#### Annotate Tree By ID using API
@app.route('/AnnotateMarkersByID/<treeid>', methods=['GET', 'POST'])
def AnnotateMarkersByID(treeid=None):
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		select = session['dataset']
		cols_pano = db[select+"_panos"]
		idd = str(treeid)

		cols_trees =  db[select]
		col_tree = cols_trees.find_one({'_id': ObjectId(idd)})
		del col_tree['_id']
		classes = db['classes'].find()
		classes = list(classes)

		lat = col_tree['location']['coordinates'][1]
		lng = col_tree['location']['coordinates'][0]
		subid = treeid
		session['idd'] = idd
		session['lat'] = lat
		session['lng'] = lng

		cols_trees =  db[select]
		col_tree = cols_trees.find_one({'_id': ObjectId(idd)})
		del col_tree['_id']
		data = crawl_all_panos(float(lat), float(lng), 100)
		payload = []
		for x in data:
			col = cols_pano.find_one({ '$and' : [{'_id': x['pano']['Location']['panoId']},{ "annotated" : { "$exists" : False } }]})
			if col != None:
				payload.append(col)
			else:
				payload.append({'_id':x['pano']['Location']['panoId'],"annotations":[],"pano_details":x['pano'], "x":x['x'], "y":x['y'],"lat":x['lat'],"lng":x['lng']})

		idd = [{"id":idd}]
		return render_template('AnnotateMarkers.html', data=payload, classes=classes, tree_id = idd, tree = col_tree,  t=title, h=subid)


@app.route('/UpdateTreeAnnotation', methods=['GET', 'POST'])
def UpdateTreeAnnotation():
	d = "failed"
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		select = session['dataset']
		data = request.json
		cols_pano = db[select+"_panos"]
		cols = db[select]
		panos = data[0]
		annotations = data[1]
		try:
			for i in range(len(data[0])):
				pano_id = panos[i]['Location']['panoId']
				pano_details = panos[i]
				annotation = annotations[i]
				# print({'pano_id':pano_id,'pano_details':pano_details,'annotations':annotation})
				print({'pano_id':pano_id})
				cols_pano.update({'_id':pano_id},{'$set': {'annotations': annotation,"pano_details":pano_details}}, upsert=True)
				cols.find_one_and_update({"_id": ObjectId(data[2][0]['id'])}, {"$set": {"annotated":"yes","user":session['user'],"panos":panos,"created_date":datetime.now()}})
			d = "success"
		except:
			d = "failed"
		return jsonify(
	        response = d)

@app.route('/GetBoundsMarkers', methods=['GET', 'POST'])
def GetBoundsMarkers():
	try:
		docs = []
		select = session['dataset']
		cols = db[select]
		data = request.json

		bound_data = cols.find({
			     'location': {
			       '$geoWithin': {
			          '$geometry': {
			             'type' : 'Polygon' ,
			             'coordinates': [[
			                        [ data['west'], data['north'] ],
			                        [ data['west'], data['south'] ],
			                        [ data['east'], data['south'] ],
			                        [ data['east'], data['north'] ],
			                        [ data['west'], data['north'] ]
			                           ]]
			       }
			     }
			   }
			})

		for document in bound_data:
			tmp = str(document['_id'])
			del document['_id']
			document['_id'] = tmp
			docs.append(document)

		d = docs
	except:
		d = "failed"
	return jsonify(
        response = d)

@app.route('/UpdateMarker', methods=['GET', 'POST'])
def UpdateMarker():
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		id = ""
		try:
			select = session['dataset']
			cols = db[select]
			data = request.json
			cols.find_one_and_update({"_id": ObjectId(data["id"])},{"$set": {"location": {"type":"Point","coordinates":[data["lng"],data["lat"]]}}}, upsert=False)
			d = "success"
		except:
			d = "failed"
		return jsonify(
	        response = d)

@app.route('/NewMarker', methods=['GET', 'POST'])
def NewMarker():
	if session['user'] == None or session['user'] == "":
		return redirect(url_for('index'))
	else:
		d = ""
		try:
			select = session['dataset']
			cols = db[select]
			data = request.json
			cols.insert({'location':{'coordinates':[data['lng'],data['lat']],'type':"Point"},'Specie':None})
			d = "success"
		except:
			d = "failed"
		return jsonify(
	        response = d)

@app.route('/DeleteMarker', methods=['GET', 'POST'])
def DeleteMarker():
	d = ""
	select = session['dataset']
	cols = db[select]
	data = request.json
	t = cols.remove({"_id": ObjectId(data['id'])})
	d = "success"
	# except:
	# 	d = "failed"
	return jsonify(
        response = d)

@app.route("/DownloadAnnot/<treeid>", methods=['GET', 'POST'])
def DownloadAnnot(treeid=None):
    # with open("outputs/Adjacency.csv") as fp:
    #     csv = fp.read()
	db = cl.db
	tree_col = db['pasadena'].find({"_id":ObjectId(treeid)})
	tree_col = list(tree_col)
	tree_col = list(tree_col)[0]
	panos = tree_col['panos']
	annotations = []
	loc = [tree_col["location"]["coordinates"][1],tree_col["location"]["coordinates"][0]]

	for i in range(len(panos)):
		pano = db['pasadena_panos'].find({"_id":panos[i]})
		annot = []
		pano = list(pano)[0]
		maintree = tree_col['boxesids'][i]
		annotation = ""
		if len(pano['boxes']) == 1:
			annotation = create_single_annot(pano['_id'],pano['boxes'],maintree,loc)
		else:
			annotation = create_multi_annot(pano['_id'],pano['boxes'],maintree,loc)
		annotations.append(annotation)
	d = "Download"
	return jsonify(
	        response = d)


if __name__ == '__main__':
	app.secret_key = 'APP SECRET KEY'
#	app.run(debug=True,host="0.0.0.0",port=80)
	bcrypt = Bcrypt(app)

	app.run(debug=True)
