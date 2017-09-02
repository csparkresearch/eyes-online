from app import app,SQLAlchemy,db
from app.db_handler import User,UserScript
from flask import Flask, render_template,request,json,session,redirect,jsonify,send_from_directory
from werkzeug import generate_password_hash, check_password_hash
import os,random
from flasgger.utils import swag_from

@app.route('/signUp',methods=['POST'])
@swag_from('signUp.yml')
def signUp():
    # read the posted values from the UI
    print (request)
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']

    # validate the received values
    if _name and _email and _password:
	    _hashed_password = generate_password_hash(_password)
	    newUser = User(_email, _name,_hashed_password)
	    try:
		    db.session.add(newUser)
		    db.session.commit()
		    return json.dumps({'status':True,'message':'User %s created successfully. e-mail:%s !'%(_name,_email)})
	    except Exception as exc:
		    reason = str(exc)
		    return json.dumps({'status':False,'message':str(reason)})


@app.route('/validateLogin',methods=['POST'])
@swag_from('validateLogin.yml')
def validateLogin():
    _username = request.form['inputEmail']
    _password = request.form['inputPassword']
    user = User.query.filter_by(email=_username).first() #retrieve the row based on e-mail
    if user is not None:
        if check_password_hash(user.pwHash,_password):
            session['user'] = [user.username,user.email]
            return json.dumps({'status':True,'message':'Login successful'})
        else:
            return json.dumps({'status':False,'message':'Wrong Email address or Password. hash mismatch'})
    else:
        return json.dumps({'status':False,'message':'User not found'})

@app.route('/logout',methods=['PUT'])
@swag_from('logout.yml')
def logout():
	try:
		if session.get('user'):
			return json.dumps({'status':True,'message':'Logged out'})
		else:
			return json.dumps({'status':True,'message':"You weren't logged in"})
	except Exception as exc:
		reason = str(exc)
		return json.dumps({'status':False,'message':str(reason)})


@app.route('/getUserName')
@swag_from('getUserName.yml')
def getUserName():
	if session.get('user'):
		return json.dumps({'status':True,'username':session['user'][0],'email':session['user'][1]})
	else:
		return json.dumps({'status':False,'username':'','email':''})


@app.route('/addScript',methods=['POST'])
@swag_from('addScript.yml')
def addScript():
	try:
		if session.get('user'):
			_email = session.get('user')[1]
			_title = request.form['inputTitle']
			_description = request.form['inputDescription']
			_doc_type = request.form.get('inputType','code')

			newSnippet = UserScript(_email, _title,_description,_doc_type)
			try:
				db.session.add(newSnippet)
				db.session.commit()
				return json.dumps({'status':True,'message':'stored'})
			except Exception as exc:
				return json.dumps({'status':False,'message':str(exc)}),403

		else:
			return json.dumps({'status':False,'message':'Unauthorized access'}),401
	except Exception as e:
		return json.dumps({'status':False,'message':str(e)}),400




@app.route('/updateScript', methods=['POST'])
@swag_from('updateScript.yml')
def updateScript():
  if session.get('user'):
    _email = session.get('user')[1]
    _title = request.form['inputTitle']
    _description = request.form['inputDescription']
    _script_id = request.form['codeId']
    try:
      script = UserScript.query.filter_by(email=_email,id=_script_id).first()
      script.title = _title
      script.script = _description
      db.session.commit()
      return json.dumps({'status':True,'message':'Updated!'})
    except Exception as exc:
      return json.dumps({'status':False,'message':str(exc)})
  else:
    return json.dumps({'status':False,'message':'Unauthorized access'})




@app.route('/deleteScript',methods=['POST'])
@swag_from('deleteScript.yml')
def deleteScript():
  if session.get('user'):
    _email = session.get('user')[1]
    _id = request.form['scriptId']
    try:
      UserScript.query.filter_by(email=_email,id=_id).delete()
      db.session.commit()
      return json.dumps({'status':True,'message':'Deleted!'}),200
    except Exception as exc:
      return json.dumps({'status':False,'message':str(exc)}),403
  else:
    return json.dumps({'status':False,'message':'Unauthorized access'}),401


@app.route('/getScriptList')
@swag_from('getScriptList.yml')
def getScriptList():
	try:
		if session.get('user'):
			_email = session.get('user')[1]
			scripts = UserScript.query.filter_by(email=_email,doc_type='code')
			scripts_dict = []
			for script in scripts:
				single_script = {
						'Id': script.id,
						'Filename': script.title,
						#'Code': script.script, #Can be enbled if the user demands all scripts and content.
						'Date': script.pub_date}
				scripts_dict.append(single_script)
			return json.dumps({'status':True,'data':scripts_dict,'message':'done'}),200
		else:
			return json.dumps({'status':False,'data':[],'message':'Please login first'}),401
	except Exception as e:
		print (str(e))
		return json.dumps({'status':False,'data':[],'message':str(e)}),403


@app.route('/getDocList')
@swag_from('getDocList.yml')
def getDocList():
	try:
		if session.get('user'):
			_email = session.get('user')[1]
			scripts = UserScript.query.filter_by(email=_email,doc_type='doc')
			scripts_dict = []
			for script in scripts:
				single_script = {
						'Id': script.id,
						'Filename': script.title,
						#'Code': script.script, #Can be enbled if the user demands all scripts and content.
						'Date': script.pub_date}
				scripts_dict.append(single_script)
			return json.dumps({'status':True,'data':scripts_dict,'message':'done'}),200
		else:
			return json.dumps({'status':False,'data':[],'message':'Please login first'}),401
	except Exception as e:
		return json.dumps({'status':False,'data':[],'message':str(e)}),403


@app.route('/getScriptById',methods=['POST'])
@swag_from('getScriptById.yml')
def getScriptById():
	if session.get('user'):
		_id = request.form['id']
		_email = session.get('user')[1]
		try:
			script = UserScript.query.filter_by(email=_email,id=_id).first()
			return json.dumps({'status':True,'Code':script.script,'Filename':script.title,'Date':script.pub_date,'message':'got script %s'%script.title})
		except Exception as exc:
			print (exc)
			return json.dumps({'status':False,'message':str(exc),'Filename':'','Date':'','Code':''}),403
	else:
		return json.dumps({'status':False,'message':'Unauthorized access','Filename':'','Date':'','Code':''}),401


@app.route('/getPublicScripts')
@swag_from('getPublicScripts.yml')
def getPublicScripts():
	try:
		admins = User.query.filter_by(authorized = True)
		data = {}
		staticdata = {}
		for admin in admins:
			scripts = UserScript.query.filter_by(email=admin.email,doc_type='code')
			scripts_dict = []
			for script in scripts:
				single_script = {
						'Id': script.id,
						'Filename': script.title,
						#'Code': script.script, #Can be enbled if the user demands all scripts and content.
						'Date': script.pub_date}
				scripts_dict.append(single_script)
			data[admin.username] = scripts_dict

		for dirname in ['scripts']:
			scripts_dict = []
			for a in os.listdir(os.path.join('.','app','static',dirname)):
				if a[-3:]=='.py':
					scripts_dict.append({'Filename':a})
			staticdata[dirname] = scripts_dict

		return json.dumps({'status':True,'data': data,'staticdata': staticdata, 'message':'done'}),200
	except Exception as e:
		print (str(e))
		return json.dumps({'status':False,'data':{},'message':str(e)}),403





@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

