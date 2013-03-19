'''
Created in February 2013

@summary: A Plex Media Server plugin that integrates Tumblr into the Plex picture container.
@version: 0.1
@author: hodgers
'''

from master_list import items

PLUGIN_TITLE						= "Tumblr photos"		# The plugin Title
PLUGIN_PREFIX   					= "/photos/tumblr"		# The plugin's contextual path within Plex
PLUGIN_HTTP_CACHE_INTERVAL			= 0

# Plugin Icons

PLUGIN_ICON_DEFAULT					= "icon-default.png"
PLUGIN_ART							= "art-default.jpg"
#PLUGIN_ICON_ABOUT					= "icon-about.png"
PLUGIN_ICON_PREFS					= "icon-prefs.png"
PLUGIN_ICON_MORE					= "icon-more.png"

# Tumblr-related

API_KEY								= "XOMD2cFNNEZGIaahNJKi9soBiscPssf9xX7MCDx0R2rGIgbtEy"

ITEMS_PER_PAGE						= 20
DEFAULT_OFFSET						= 0

URL_STEM							= "http://api.tumblr.com/v2/blog/"
URL_INFO							= ".tumblr.com/info"
URL_LIKES							= ".tumblr.com/likes"
URL_FOLLOWERS							= ".tumblr.com/followers"
URL_POSTS							= ".tumblr.com/posts"
URL_API								= "/?api_key=" + API_KEY
URL_LIMIT							= "&limit=" + str(ITEMS_PER_PAGE)

####################################################################################################



def Start():

	Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE, PLUGIN_ICON_DEFAULT, PLUGIN_ART)
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("Gallery", viewMode="Pictures", mediaType="photos")
	
	ObjectContainer.art = R(PLUGIN_ART)
	ObjectContainer.title1 = PLUGIN_TITLE
	#DirectoryObject.thumb = R(PLUGIN_ICON_DEFAULT)

	HTTP.CacheTime = PLUGIN_HTTP_CACHE_INTERVAL



def MainMenu(query='',type=''):

	if query:
		Log(" ".join(["Adding",type,query]))
		if type == 'tag':
			items.append("Tag: " + query)
		else:
			items.append(query)
	query = ''
	type = ''
	
	string = ",".join(items)
	
	dir = ObjectContainer(replace_parent=True)
	dir.art = R(PLUGIN_ART)
	
	# Manually entered
	dir.add(
		InputDirectoryObject(
			key = Callback(MainMenu, type='tumblr'),
			title = '> Add a Tumblr',
			prompt = "[__________].tumblr.com",
			thumb = R(PLUGIN_ICON_DEFAULT)
		)
	)
	
	# Tag
	dir.add(
		InputDirectoryObject(
			key = Callback(MainMenu, type='tag'),
			title = '> Add a tag',
			prompt = "Tag",
			thumb = R(PLUGIN_ICON_DEFAULT)
		)
	)
	
	# Settings
	dir.add(
		PrefsObject(
			title = '> Settings',
			tagline = 'Set your favourite Tumblr',
			summary = 'Settings',
			thumb = R(PLUGIN_ICON_DEFAULT)
		)
	)

	# Default user
	if Prefs['username']:  

		try:
			TumblrInfo = JSON.ObjectFromURL(FormURL(Prefs['username'] + URL_INFO))['response']['blog']
			Log("Default info: " + TumblrInfo['description'])

			thumb = URL_STEM + Prefs['username'] + ".tumblr.com/avatar/512"
	
			art = ""
			try:
				art = JSON.ObjectFromURL(FormURL(Prefs['username'] + URL_POSTS + "/photo"))['response']['posts'][0]['photos'][0]['original_size']['url']
			except:
				pass
			Log("Default art: " + art)

			dir.add(
				PopupDirectoryObject(
					key = Callback(
						Selection,
						tumblr = Prefs['username']
					),
					title = "From settings: " + Prefs['username'],
					thumb = thumb,
					art = art,
					summary = TumblrInfo['description']
				)
			)
		except: pass
	
	# Following
	#dir.Append(Function(DirectoryObject(Following, title='Following', thumb=R(PLUGIN_ICON_DEFAULT), summary='Following')))
	
	for item in items:
	
		Process(dir,item)
	
	return dir



def Process(dir,item):

	
	Log("Example: " + item)

	if "Tag: " in item:
	
		perfecttag = item.replace('Tag: ','')
		perfecttag = perfecttag.replace(' ','%20')
	
		tagurl = 'http://api.tumblr.com/v2/tagged?tag=' + perfecttag + '&api_key=' + API_KEY
		Log("Tag URL: " + tagurl)
	
		dir.add(
			DirectoryObject(
				key = Callback(
					DisplayMedia,
					url = tagurl,
					action = 'tag',
					title = item
				),
				title = item
			)
		)
		
	else:
	
		TumblrInfo = JSON.ObjectFromURL(FormURL(item + URL_INFO))['response']['blog']
		Log("Info: " + TumblrInfo['description'])

		thumb = URL_STEM + item + ".tumblr.com/avatar/512"

		art = ""
		try:
			art = JSON.ObjectFromURL(FormURL(item + URL_POSTS + "/photo"))['response']['posts'][0]['photos'][0]['original_size']['url']
		except:
			pass
		Log("Art: " + art)

		dir.add(
			PopupDirectoryObject(
				key = Callback(
					Selection,
					tumblr = item
				),
				title = "Tumblr: " + item,
				thumb = thumb,
				art = art,
				summary = TumblrInfo['description']
			)
		)
		
	return dir


def Selection(tumblr):

	dir = ObjectContainer()
	dir.title1 = 'Choose...'
	
	dir.add(
		DirectoryObject(
			key = Callback(
				DisplayMedia,
				url = FormURL(tumblr + URL_POSTS),
				action = 'blog'
			),
			title = 'Posts'
		)
	)
	
	dir.add(
		DirectoryObject(
			key = Callback(
				DisplayMedia,
				url = FormURL(tumblr + URL_LIKES),
				action = 'likes'
			),
			title = 'Likes (if available)'
		)
	)
	
# 	dir.add(
# 		DirectoryObject(
# 			key = Callback(
# 				DisplayMedia,
# 				url = FormURL(tumblr + URL_FOLLOWERS),
# 				action = 'followers'
# 			),
# 			title = 'Followers'
# 		)
# 	)
# 	
	return dir


def DisplayMedia(url, action, title = '', offset = DEFAULT_OFFSET):

# 	dir.add(
# 		PopupDirectoryObject(
# 			key = Callback(
# 				DisplayMedia,
# 				url = url,
# 				offset = str(newoffset)
# 			),
# 			title = "More...",
# 			thumb = R(PLUGIN_ICON_DEFAULT)
# 		)
# 	)

	url = url + "&offset=" + str(offset)
	Log("URL: " + url)
	dir = ObjectContainer()
	json = JSON.ObjectFromURL(url)
	
	dir.title1 = ""
	if action == 'likes':
		dir.title1 = 'Likes'
		children = json['response']['liked_posts']
	elif action == 'tag':
		dir.title1 = title
		children = json['response']
	else:
		action = 'blog'
		dir.title1 = "Posts: " + json['response']['blog']['title']
		children = json['response']['posts']

	if len(children) != 0:
		
		for num in range(len(children)):
			child = children[num]
		
			type = JSON.StringFromObject(child['type'])
			Log("Type: " + type)
		
			title = "From "
			try:
				title = title + str(child['source_title'])
			except KeyError:
				title = title + "nowhere"
			title = title + " (" + str(child['note_count']) + ")"
			
			if "photo" in type:

				PhotoURL = child['photos'][0]['original_size']['url']
				Log("Photo URL: " + PhotoURL)
		
				try:
					permalink = JSON.StringFromObject(child['image_permalink'])
				except KeyError:
					permalink = PhotoURL

				Log("Photo permalink: " + permalink)
		
				dir.add(
					PhotoAlbumObject(
						url = permalink,
						title = title,
						thumb = PhotoURL,
						art = PhotoURL
					)
				)
	
			if "video" in type:

				try:
					permalink = JSON.StringFromObject(child['post_url'])
				except AttributeError:
					permalink = child['video_url']

				Log("Video permalink: " + permalink)
		
				try:
					dir.add(
						PhotoAlbumObject(
							url = child['video_url'],
							title = title,
							thumb = str(child['thumbnail_url'])
						)
					)
				except:
					pass
					

	if action != 'tag':
	
		newoffset = int(offset) + ITEMS_PER_PAGE

		dir.add(
			DirectoryObject(
				key = Callback(
					DisplayMedia,
					url = url,
					action = action,
					offset = str(newoffset)
				),
				title = "More...",
				thumb = R(PLUGIN_ICON_DEFAULT)
			)
		)
	
	return dir



def FormURL(middle):

	url = URL_STEM + middle + URL_API + URL_LIMIT
	
	return url


def ValidatePrefs():

	query = ''
	type =''

	return MainMenu(query = '', type = '')