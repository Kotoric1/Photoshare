import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
from collections import Counter
import flask_login
from datetime import date
#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'kotoric1025'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	try:
		users = getUserList()
		email = request.form.get('email')
		if not(email) or email not in str(users):
			return
		user = User()
		user.id = email
		cursor = mysql.connect().cursor()
		cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		user.is_authenticated = request.form['password'] == pwd
		return user

	except Exception as e:
		print(e)
		return

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		first_name=request.form.get('firstname')
		last_name=request.form.get('lastname')
		birthday=request.form.get('birthday')
		hometown=request.form.get('hometown')
		gender=request.form.get('gender')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users ( email, password, first_name, last_name, birthday, hometown, gender) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(email, password,first_name, last_name, birthday, hometown, gender)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('profile.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return render_template('register.html', message='Account Created!')	

def user_ids_list():
	cursor = conn.cursor()
	cursor.execute("""SELECT user_id from Users """)
	records = cursor.fetchall()
	# all user ids in list form
	records_list = [x[0] for x in records]
	return records_list

def user_email_list():
	cursor = conn.cursor()
	cursor.execute("""SELECT email from Users """)
	records = cursor.fetchall()
	# all user ids in list form
	records_list = [x[0] for x in records]
	return records_list

def tags_list():
	cursor = conn.cursor()
	cursor.execute("""SELECT tag_id from Tags """)
	records = cursor.fetchall()
	# all tag ids in list form
	records_list = [x[0] for x in records]
	return records_list

def getUniquePhotosFromTag(tag_id_list):
	all_photos = []
	for tag in tag_id_list:
		all_photos = all_photos + [i for i in photos_from_tags(tag)]

	unique_photos = [] 
	for i in all_photos: 	
		if i not in unique_photos: 
			unique_photos.append(i) 

	return unique_photos


def getUsersPhotos(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id,  caption FROM Photos WHERE user_id = '{0}'".format( user_id))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def user_photo_ids(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id FROM Photos WHERE user_id = '{0}'".format( user_id))
	return cursor.fetchall()[0]

def comments_on_photos(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id, text FROM Comments  WHERE photo_id = '{0}'".format(photo_id))
	a = cursor.fetchall()
	comments_list = [ [x[0], x[1]] for x in a]
	return comments_list

def photo_info(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT data,  photo_id, caption FROM Photos WHERE photo_id = '{0}'".format(photo_id))
	return cursor.fetchall()

def albums_photos(album_name):
	cursor = conn.cursor()
	cursor.execute(" SELECT data, photo_id,  caption FROM Photos WHERE album_name = '{0}'".format(album_name))
	return cursor.fetchall()

def user_albums(user_id):
	cursor = conn.cursor()
	cursor.execute("Select album_name FROM Albums_have  WHERE user_id = '{0}'".format(user_id))
	a = cursor.fetchall()
	albums_list = [x[0] for x in a]
	albums_list = [x for x in  albums_list if x != None ]
	return albums_list

def user_friends(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT friend_id  FROM Friends WHERE user_id = '{0}'".format(user_id ))
	friends = cursor.fetchall()
	friend_list = [x[0] for x in friends]
	return friend_list

def mutual_friend(current_id, friend_id):
	cursor = conn.cursor()
	cursor.execute("SELECT friend_id FROM Friends WHERE user_id != '{0}' AND user_id = '{1}' ".format(current_id, friend_id))
	mutual = cursor.fetchall()
	mutual_list = [x[0] for x in mutual]
	return mutual_list

def recommend_friends(current_id):
	friend_list = user_friends(current_id)
	mutual_friends = []
	for friend in friend_list:
		mutual_friends += mutual_friend(current_id, friend)

	return mutual_friends

def count_comments(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(comment_id) FROM Comments WHERE user_id = '{0}'".format(user_id))
	count = cursor.fetchall()
	count_total = [x[0] for x in count]
	return count_total

def count_photos(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(photo_id) FROM Photos WHERE user_id = '{0}'".format(user_id))
	count = cursor.fetchall()
	count_total = [x[0] for x in count]
	return count_total

def user_activity(user_id):
	print("FROM TOTALUSER ACTIVITY", count_comments(user_id) +count_photos(user_id))
	return sum(count_comments(user_id) + count_photos(user_id))
	
def top10Contributors():
	user_ids = user_ids_list()
	contribution = []
	for user in user_ids:
		contribution = contribution + [(user_activity(user), user)]
	print(contribution)
	contribution.sort()
	contribution.reverse()
	top10 = []

	for i in contribution:
		top10.append(email_from_user_id(i[1]))

	top10_users = [x[0] for x in top10]

	return top10_users

def email_from_user_id(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT email FROM Users WHERE user_id = '{0}'".format(user_id))
	records = cursor.fetchall()
	records_list = [x[0] for x in records]
	return records_list

def user_id_from_photo_id(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Photos WHERE  photo_id = '{0}'".format(photo_id))
	return cursor.fetchall()[0]

#def getLastNameFromUser_Id(user_id):
	#cursor = conn.cursor()
	#cursor.execute("SELECT last_name FROM Users WHERE user_id = '{0}'".format(user_id))
	#return cursor.fetchone()[0]

# def getFirstNameFromUser_Id(user_id):
# 	cursor = conn.cursor()
# 	cursor.execute("SELECT first_name FROM Users WHERE user_id = '{0}'".format(user_id))
# 	return cursor.fetchone()[0]

def photos_from_tags(tag_id):
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id FROM Tagged WHERE tag_id = '{0}'".format(tag_id))
	records = cursor.fetchall()
	records_list = [x[0] for x in records]
	return records_list

def num_photos_from_tags(tag_id):
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id FROM Tagged WHERE tag_id = '{0}'".format(tag_id))
	records = cursor.fetchall()
	records_list = [x[0] for x in records]
	return len(records_list)

def photos_from_taglist(tag_id_list):
	photo_list = []
	length = len(tag_id_list)
	for tag in tag_id_list:
		photo_list = photo_list + [x for x in photos_from_tags(tag)]
	result = []
	A = Counter(photo_list)
	
	for key, value in A.items():
		if value == length:
			result.append(key)
	return result


def tag_id_from_photo_id(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_id FROM Tagged WHERE photo_id = '{0}'".format(photo_id))
	records = cursor.fetchall()
	tag_id_list = [x[0] for x in records]
	return tag_id_list


def photos_from_photo_id(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id, caption FROM Photos WHERE photo_id = '{0}'".format(photo_id))
	return cursor.fetchall()
	#markkk

def tag_from_tag_id(tag_id):
	cursor = conn.cursor()
	cursor.execute("SELECT word FROM Tags WHERE tag_id = '{0}'".format(tag_id))
	return cursor.fetchone()[0]

def tag_id_from_tag(word):
	print(" this is name: ", word)
	cursor = conn.cursor()
	cursor.execute("SELECT tag_id FROM Tags WHERE word = '{0}'".format(word))
	x = cursor.fetchone()
	print("this is x: ", x)
	print("this is x[0]: ", x[0])
	return x[0]
	
	
def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def photo_id_from_caption(caption):
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id  FROM Photos WHERE caption = '{0}'".format(caption))
	return cursor.fetchone()[0]

def album_id_from_user_id(user_id, album_name):
	cursor = conn.cursor()
	cursor.execute("SELECT albums_id FROM Albums_have WHERE user_id = '{0}' AND album_name = '{1}' ".format(user_id, album_name))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

def delete_album(album_name):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Albums_have WHERE album_name = '{0}'".format(album_name))
	conn.commit()
	print("Album has been deleted!")
	return "Deleted"

def delete_photo(photo_id):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Photos WHERE photo_id = '{0}'".format(photo_id))
	conn.commit()
	print("Photo has been deleted!")
	return "Deleted"


def insert_like(user_id, photo_id):
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Likes (photo_id, user_id) VALUES (%s, %s)", (photo_id, user_id))
	conn.commit()
	return "inserted"

def like_count(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(*) FROM Likes WHERE photo_id = '{0}'".format(photo_id))
	return cursor.fetchall()[0]


def like_list(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Likes WHERE photo_id = '{0}'".format(photo_id))
	ids = cursor.fetchall()
	ids_list = [x[0] for x in ids]
	emails_list = [email_from_user_id(y) for y in ids_list]
	return emails_list

def isTagUnique(word):
	#use this to check if a tag has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT word FROM Tags WHERE word = '{0}'".format(word)):
		#this means there are greater than zero entries with that tag
		return False
	else:
		return True	
#end login code

#400

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('profile.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		image= request.files['photo']
		data =image.read()
		caption = request.form.get('caption')
		album_name= request.form.get('album_name')
		album_id = album_id_from_user_id(user_id, album_name)
		tags = request.form.get('tags')
		tags = tags.split(",")
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Photos (data, user_id, caption, albums_id,  album_name) VALUES (%s, %s, %s, %s, %s ) ''' ,( data, user_id, caption, album_id, album_name))
		conn.commit()

		for i in tags:
			if isTagUnique(i):
				cursor = conn.cursor()
				cursor.execute('''INSERT INTO Tags (word) VALUES (%s) ''' ,(i))
				conn.commit()

			tag_id = tag_id_from_tag(i)
			photo_id = photo_id_from_caption(caption)
			cursor = conn.cursor()
			cursor.execute('''INSERT INTO Tagged (photo_id,tag_id) VALUES (%s,%s) ''' ,(photo_id, tag_id))
			conn.commit()

		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(user_id), Albums = user_albums(user_id),base64=base64)

	else:
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		# print(" Arriving at GET upload method")
		return render_template('upload.html', Albums = user_albums(user_id))
#end photo uploading code



@app.route ("/album", methods=['GET','POST'])
@flask_login.login_required
def album():
	if request.method == 'POST':
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		album_name= request.form.get('album_name')
		albums=user_albums(user_id)
		date1 = date.today()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Albums_have ( album_name, date, user_id) VALUES (%s, %s, %s ) ''' ,(album_name, date1, user_id))
		conn.commit()
		for album in albums:
			print(album)
		if request.form.get("2")=="Delete":
			deleted_album = request.form.get('album_delete')
			delete_album(deleted_album)
			return render_template('album.html', name=flask_login.current_user.id, albums=user_albums(user_id), message="Album deleted!",base64=base64)
		else:
			return render_template('album.html', name=flask_login.current_user.id, albums=user_albums(user_id), message="Album added!",base64=base64)

	else:
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		print("Got to GET method of /album")
		return render_template('album.html', albums=user_albums(user_id))



@app.route("/show_photos", methods=["GET"])
def allphotos():

	uids = user_ids_list()

	photos = []
	for uid in uids:
		photos = photos + [getUsersPhotos(uid)]
	
	return render_template('show_photos.html', AllPhotos=photos, base64=base64)

@app.route("/show_myphotos", methods=["GET"])
@flask_login.login_required
def myphotos():

	uid = getUserIdFromEmail(flask_login.current_user.id)

	photos = []
	photos = photos + [getUsersPhotos(uid)]
	
	return render_template('show_myphotos.html', photos = getUsersPhotos(uid), base64=base64)

@app.route("/search_tags", methods=["GET"])
def search_tags():
	tag_list = tags_list()
	tags = []
	for tag_id in tag_list:
		tags = tags + [tag_from_tag_id(tag_id) ]

	return render_template('search_tags.html', tags=tags )

@app.route("/search_tags", methods=["POST"])
def select_tag():
	tag_list = tags_list()
	tags = []
	for tag_id in tag_list:
		tags = tags + [tag_from_tag_id(tag_id)]

	return render_template('show_album.html', tags=tags )

@app.route("/recommend", methods=["GET"])
@flask_login.login_required
def rec():
	uid_list = user_ids_list()
	photos = []
	for uid in uid_list:
		photos = photos + [x for x in user_photo_ids(uid)]
	# print(photos)
	user = getUserIdFromEmail(flask_login.current_user.id)
	mypicture = user_photo_ids(user)
	# print(mypicture)
	c = [x for x in photos if x not in mypicture]
	# print(c)
	tags = []
	for photo in mypicture:
		tags = tags + [tag_id_from_photo_id(photo) ]

	tag_ids = tags[0]
	print(tag_ids)
	photo_ids = photos_from_taglist(tag_ids)
	print(photo_ids)
	photo_ids = [x for x in photo_ids if x not in mypicture]
	print(photo_ids)
	new_photos = []
	for i in photo_ids:
		new_photos = new_photos + [x for x in photos_from_photo_id(i)]
	return render_template ('recommend.html',photos=new_photos, base64=base64)

@app.route("/recommend", methods=["POST"])
@flask_login.login_required
def recom():
	uids = user_ids_list()
	photos = []
	for uid in uids:
		photos = photos + [x for x in user_photo_ids(uid)]
	
	print(photos)

	user = getUserIdFromEmail(flask_login.current_user.id)

	mypicture = user_photo_ids(user)

	print(mypicture)

	c = [x for x in photos if x not in mypicture]

	print(c)

	tags = []
	for photo in mypicture:
		tags = tags + [tag_id_from_photo_id(photo) ]

	tag_ids = tags[0]

	print(tags[0])

	photo_ids = photos_from_taglist(tag_ids)

	print(photo_ids)

	photo_ids = [x for x in photo_ids if x not in mypicture]

	print(photo_ids)

	new_photos = []

	for i in photo_ids:
		new_photos = new_photos + [x for x in photos_from_photo_id(i)]

	return render_template ('recommend.html',photos=new_photos, base64=base64)

@app.route("/search_mytags", methods=["GET"])
@flask_login.login_required
def search_mytags():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	photos = user_photo_ids(uid)
	tags = []
	for photo in photos:
		tags = tags + [tag_id_from_photo_id(photo) ]

	return render_template('search_mytags.html', tags=tags[0] )


@app.route("/search_mytags", methods=["POST"])
@flask_login.login_required
def select_mytags():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	photos = user_photo_ids(uid)
	tags = []
	for photo in photos:
		tags = tags + [tag_id_from_photo_id(photo) ]

	return render_template('search_mytags.html', tags=tags[0] )
#635
@app.route("/show_tag_photos/<tag_name>", methods=['GET', 'POST'])
def show_tag(tag_name):
	if request.method == "GET":
		print("Tag: ", tag_name)
		tag_id = tag_id_from_tag(tag_name)
		photo_ids = photos_from_tags(tag_id)
		photos = []
		for i in photo_ids:
			photos = photos + [x for x in photos_from_photo_id(i)]

		return render_template ('show_tag_photos.html', tag_name=tag_name , photos=photos, base64=base64)
		

@app.route("/show_album", methods=["GET"])
def showallalbums():
	uids = user_ids_list()
	albums = []
	for uid in uids:
		albums = albums + [  x for x in user_albums(uid)  ]

	return render_template('show_album.html', albums=albums )

@app.route ("/search_image", methods=['GET', 'POST'])
def image_search():
	if request.method=='POST':
		tag = request.form.get('search_here')
		tag = tag.split(",")
		tag_id = []
		print("this is tagl: ", tag)
		for i in tag:
			print(" this is i", i)
			tag_id.append(tag_id_from_tag(i))
		photo_ids = getUniquePhotosFromTag(tag_id)
		photos = []

		for i in photo_ids:
			photos = photos + [x for x in photos_from_photo_id(i)]
		return render_template ('show_tag_photos.html',tag_name = tag, photos=photos, base64=base64)
	return render_template('search_image.html') 


@app.route("/show_my_album", methods=["GET"])
@flask_login.login_required
def showallmyalbums():

	uid = getUserIdFromEmail(flask_login.current_user.id)

	album = []
	album = album + [x for x in user_albums(uid)]
	
	return render_template('show_my_album.html', albums = album)

@app.route("/show_my_album", methods=["POST"])
@flask_login.login_required
def selectmyalbums():

	uid = getUserIdFromEmail(flask_login.current_user.id)

	album = []
	album = album + [x for x in user_albums(uid)]
	
	return render_template('show_my_album.html', albums = album)

@app.route("/show_album", methods=["POST"])
def selectalbum():
	uids = user_ids_list()
	albums = []
	for uid in uids:
		albums = albums + [user_albums(uid)]

	return render_template('show_album.html', albums=albums )

@app.route("/show_album_photo/<album_name>", methods=['GET', 'POST'])
def show_album_photo(album_name):
	if request.method == "GET":
		print("album name: ", album_name)
		photo = albums_photos(album_name)

		return render_template ('show_album_photo.html', album_name=album_name, photos=photo, base64=base64)

def isOwner(photo_id, user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Photos WHERE photo_id = '{0}' AND user_id = '{1}'".format(photo_id, user_id))
	users = cursor.fetchall()
	users = [x[0] for x in users]

	if (len(users) > 0):
		return (users[0] == user_id)
	return False

@app.route("/show_album_photo/<album_name>", methods=["POST"])
@flask_login.login_required
def delete_photo(album_name):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	print("this is user id:u", uid)
	photo_delete = request.form.get('photo_delete')
	print("this is id to delete:",photo_delete)

	if (isOwner(photo_delete, uid)):
		delete_photo(photo_delete)
		return render_template ('show_album_photo.html',  album_name=album_name, base64=base64)
	# else:
	# 	photo = albums_photos(album_name)
	# 	return render_template('not_your_photo.html')
	photo = albums_photos(album_name)
	return render_template ('show_album_photo.html',  album_name=album_name, photos=photo, base64=base64)

def merge(list1, list2): 

    return  tuple(zip(list1, list2))  

@app.route("/top10", methods=["GET"])
def gettop10():
	tag_list = tags_list()

	count = []
	for tag in tag_list:
		count = count + [num_photos_from_tags(tag)] 
	tags = []
	for tag_id in tag_list:
		tags = tags + [tag_from_tag_id(tag_id)]

	merged = merge(count,tags)

	sorted_data = sorted(merged)
	
	x = []
	for i in sorted_data:
   		x.append(i[1])	   
	x.reverse()
	return render_template('top10.html', tags = x)

@app.route('/user_error')
def same_user():
		return render_template('user_error.html')	

@app.route("/displayphoto/<photo_id>", methods=['GET', 'POST'])
def display_photo(photo_id):
	photos = photo_info(photo_id)
	print(" PROCESSING FUNCTION ")
	comments = comments_on_photos(photo_id)

	if (flask_login.current_user.is_authenticated):
		email = flask_login.current_user.id
		uid = getUserIdFromEmail(email)
	else:
		uid = None

	for comment in comments:
			if comment[0] == None:
				comment[0] = "anonymous"
			else:
				comment[0] = email_from_user_id(comment[0])

	if request.method == 'POST':
		datetoday = date.today()
		text= request.form.get('comment')
		# print("this is the comment:", text)

		if (uid == user_id_from_photo_id(photo_id)[0]):
			return render_template('user_error.html', message="It's your own photo!", photo_info = photos, base64=base64)
		else:
			if request.form['submit_button'] == 'Like':
				if (flask_login.current_user.is_authenticated):
					insert_like(uid, photo_id)
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Comments ( user_id, photo_id, text, date ) VALUES (%s, %s, %s, %s ) ''' ,(uid, photo_id, text, datetoday))
		conn.commit()

		print("this is commentText: ", text)
		return render_template('displayphoto.html', user_like_list = like_list(photo_id), comments=comments , num_likes= like_count(photo_id)[0], photo_info = photos, base64=base64)

	return render_template('displayphoto.html', user_like_list = like_list(photo_id), comments=comments , num_likes= like_count(photo_id)[0], photo_info = photos, base64=base64)

def get_comment(comment_text):
	print(" this is comment_text in getMatchingComment ", comment_text)
	cursor = conn.cursor()
	cursor.execute('''SELECT user_id, text FROM Comments WHERE text LIKE '%{0}%' ORDER BY user_id desc'''.format(comment_text))
	a = cursor.fetchall()
	print(" this is records: ", a)
	comments_list = [ [x[0], x[1]] for x in a]
	print("this is commemts list: ",comments_list)
	return comments_list

@app.route ("/search_comment", methods=['GET', 'POST'])
def search_comments():
	if request.method=='POST':
		text= request.form.get('comment')
		comments = get_comment(text)
		print("these are matching comments: ", comments)
		return render_template('search_comment.html', comments=comments)
	
	return render_template('search_comment.html') 


@app.route("/friend", methods=['POST'])
@flask_login.login_required
def make_friend():
	uid = getUserIdFromEmail(flask_login.current_user.id)	
	email = user_email_list()	
	friend_email = request.form.get('friend_email')	
	print(" this is friends email: ", friend_email)	
	friend_id = getUserIdFromEmail (friend_email)	
	print(" this is friend's id: ", friend_id)	
	cursor = conn.cursor()	
	cursor.execute('''INSERT INTO Friends (user_id, friend_id) VALUES (%s, %s )''', (uid, friend_id))	
		
	conn.commit()	
	friends_ids = user_friends(uid)	
	friends_emails = []	
	for friend_id in friends_ids:	
		friends_emails = friends_emails + [email_from_user_id(friend_id)]	
		
	return render_template('friend.html', user_emails=email, friends_emails=friends_emails)

@app.route("/friend", methods=['GET'])
@flask_login.login_required
def friends_list():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	friends_ids = user_friends(uid)
	emails = user_email_list()
	friends_emails = []
	for friend_id in friends_ids:
		friends_emails = friends_emails + [email_from_user_id(friend_id)]
	
	recommend = recommend_friends(uid)
	recommendation = []
	for friend in recommend:
		recommendation = recommendation + [email_from_user_id(friend)]
	print("these are the recommendations: ", recommendation)

	return render_template('friend.html', recommendation= recommendation, user_emails=emails, friends_emails=friends_emails)

@app.route("/top10_users", methods=['GET'])
def top10_users():
	return render_template('top10_users.html', top_users=top10Contributors())

#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')
	

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)

#Finished!