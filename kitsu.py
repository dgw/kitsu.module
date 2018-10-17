# -*- coding: utf-8 -*-
##	python modules
from __future__ import unicode_literals
from sopel.module import commands, example
from sopel import web
from slugify import slugify
import requests
import bleach
##	global variables
api = 'https://kitsu.io/api/edge/'
aFilter = 'anime?page[limit]=1&page[offset]=0&include=genres,animeProductions.producer,castings.person&filter[subtype]=tv,movie,ova,ona,special&fields[anime]=canonicalTitle,titles,subtype,episodeCount,startDate,slug,synopsis,averageRating,status&fields[animeProductions]=producer,role&fields[castings]=voiceActor,featured,language,person&fields[genres]=name&fields[producers]=name&filter[text]=%s'
mFilter = 'manga?page[limit]=1&page[offset]=0&include=genres,castings.person&filter[subtype]=manga,manhua,manhwa,novel&fields[manga]=canonicalTitle,titles,subtype,startDate,slug,synopsis,averageRating,status,serialization&fields[castings]=role,person&fields[genres]=name&fields[people]=name&filter[text]=%s'
uFilter = 'users?include=waifu&fields[users]=name,waifuOrHusbando,slug&fields[characters]=canonicalName&page[limit]=1&filter[name]=%s'
sFilter = '/stats?filter[kind]=anime-amount-consumed'
lFilter = '/library-entries?page[limit]=3&sort=-progressedAt,updatedAt&include=media&fields[libraryEntries]=status,progress&fields[anime]=canonicalTitle&fields[manga]=canonicalTitle'
cFilter = 'characters?fields[characters]=slug,name,description&page[limit]=1&filter[name]=%s'
###	truncate algorithm function
#def truncate_result(fetch_anime(query)):
#	if len(fetch_anime(query)) > 400:
#		last_space = fetch_anime(query).rfind(' ', 0, 400)
#		if last_space == -1:
#			fetch_anime(query) = fetch_anime(query)[:400]
#		else:
#			fetch_anime(query) = fetch_anime(query)[:last_space]
#		return fetch_anime(query)
##	anime lookup
@commands('ka')
@example('.ka Clannad')
def ka(bot, trigger):
	query = trigger.group(2) or ''
	query = slugify(query)
	bot.say(fetch_anime(query))
##	anime search query
def fetch_anime(query):
	if not query:
		return "No search query provided."
	try:
		anime = requests.get(api + aFilter % query, timeout=(15.0, 10.0))
	except requests.exceptions.ConnectTimeout:
		return "Connection timed out."
	except requests.exceptions.ConnectionError:
		return "Could not connect to server."
	except requests.exceptions.ReadTimeout:
		return "Server took too long to reply."
	try:
		anime.raise_for_status()
	except requests.exceptions.HTTPError as e:
		return "HTTP error: " + e.message
	try:
		Data = anime.json()
	except ValueError:
		return anime.content
	try:
		Entry = Data['data'][0]
		title = Entry['attributes'].get('canonicalTitle','None')
		enTitle = Entry['attributes']['titles'].get('en',None)
		if enTitle and not enTitle == title:
			title += ' ({enTitle})'.format(enTitle=enTitle)
		status = Entry['attributes'].get('status','Unknown')
		statmaps = {'current':'Airing', 'finished':'Finished Airing', 'tba':'TBA', 'unreleased':'Unreleased', 'upcoming':'Upcoming'}
		subtype = Entry['attributes'].get('subtype')
		submaps = {'TV':'TV', 'movie':'Movie', 'OVA':'OVA', 'ONA':'ONA', 'special':'Special'}
		count = Entry['attributes'].get('episodeCount','Unknown')
		date = Entry['attributes'].get('startDate','Unknown')[:4]
		slug = Entry['attributes'].get('slug')
		rating = Entry['attributes'].get('averageRating')
		synopsis = Entry['attributes'].get('synopsis','None found.')[:140]
	except IndexError:
		return "No results found."
	try:
		included = Data.get('included')
	except IndexError:
		return
	try:
		genre = [each['attributes']['name'] for each in included if each['type'] == 'genres']
	except IndexError:
		return
	try:
		studioID = [each['relationships']['producer']['data']['id'] for each in included if each['attributes'].get('role') == 'studio']
	except IndexError:
		return
	try:
		studioName = list(set([each['attributes']['name'] for each in included if each['id'] in studioID]))
	except IndexError:
		return
	try:
		vaID = list(set([each['relationships']['person']['data']['id'] for each in included if each['attributes'].get('voiceActor') and each['attributes'].get('featured') and each['attributes'].get('language') == 'Japanese']))
	except IndexError:
		return
	try:
		vaName = list(set([each['attributes']['name'] for each in included if each['id'] in vaID]))
	except IndexError:
		return
##	anime search results output
	return "{title} ({date}) | {subtype} | Studio: {studioName} | Score: {rating} | {status} | Eps: {count} | https://kitsu.io/anime/{slug} | Genre{genreplural}: {genre} | VA: {vaName} | Synopsis: {synopsis}".format(title=title, date=date, subtype=submaps[subtype], studioName=", ".join(studioName[:-2] + [" & ".join(studioName[-2:])]), rating=rating, status=statmaps[status], count=count, slug=slug, genreplural=('' if len(genre) == 1 else 's'), genre=", ".join(genre[:-2] + [" & ".join(genre[-2:])]), vaName=", ".join(vaName[:-2] + [" & ".join(vaName[-2:])]) or "(unavailable)", synopsis=synopsis.replace("\n", " "))
##	manga lookup
@commands('km')
@example('.km One Punch Man')
def km(bot, trigger):
	query = trigger.group(2) or ''
	query = slugify(query)
	bot.say("%s" % fetch_manga(query))
##	manga search query
def fetch_manga(query):
	if not query:
		return "No search query provided."
	try:
		manga = requests.get(api + mFilter % query, timeout=(15.0, 10.0))
	except requests.exceptions.ConnectTimeout:
		return "Connection timed out."
	except requests.exceptions.ConnectionError:
		return "Could not connect to server."
	except requests.exceptions.ReadTimeout:
		return "Server took too long to reply."
	try:
		manga.raise_for_status()
	except requests.exceptions.HTTPError as e:
		return "HTTP error: " + e.message
	try:
		Data = manga.json()
	except ValueError:
		return manga.content
	try:
		Entry = Data['data'][0]
		title = Entry['attributes'].get('canonicalTitle','None')
		enTitle = Entry['attributes']['titles'].get('en',None)
		if enTitle and not enTitle == title:
			title += ' ({enTitle})'.format(enTitle=enTitle)
		status = Entry['attributes'].get('status','Unknown')
		statmaps = {'current':'Publishing', 'finished':'Completed Publishing', 'tba':'TBA', 'unreleased':'Unreleased', 'upcoming':'Upcoming'}
		subtype = Entry['attributes'].get('subtype')
		submaps = {'doujin':'Doujin', 'manga':'Manga', 'manhua':'Manhua', 'manhwa':'Manhwa', 'novel':'Novel', 'oel':'Oel', 'oneshot':'Oneshot'}
		date = Entry['attributes'].get('startDate','Unknown')[:4]
		slug = Entry['attributes'].get('slug')
		rating = Entry['attributes'].get('averageRating')
		synopsis = Entry['attributes'].get('synopsis','None found.')[:140]
	except IndexError:
		return "No results found."
	try:
		included = Data.get('included')
	except IndexError:
		return
	try:
		if included:
			genre = [each['attributes']['name'] for each in included if each['type'] == 'genres']
		else:
			genre = ['None']
	except IndexError:
		return
	try:
		if included:
			people = [each['attributes']['name'] for each in included if each['type'] == 'people']
		else:
			people = ['None']
	except IndexError:
		return
###	manga search results output
	return "{title} ({date}) | {subtype} | Author{authorplural}: {people} | Score: {rating} | {status} | https://kitsu.io/manga/{slug} | Genre{genreplural}: {genre} | Synopsis: {synopsis}...".format(title=title, date=date, subtype=submaps[subtype], rating=rating, status=statmaps[status], slug=slug, synopsis=synopsis.replace("\n", " "), genreplural=('' if len(genre) == 1 else 's'), genre=", ".join(genre[:-2] + [" & ".join(genre[-2:])]), authorplural=('' if len(people) == 1 else 's'), people=", ".join(people[:-2] + [" & ".join(people[-2:])]))
##	user lookup
@commands('ku')
@example('.ku SleepingPanda')
def ku(bot, trigger):
	query = trigger.group(2) or None
	bot.say("%s" % fetch_user(query))
##	user search query
def fetch_user(query):
	if not query:
		return "No search query provided."
	try:
		user = requests.get(api + uFilter % query, timeout=(10.0, 4.0))
	except requests.exceptions.ConnectTimeout:
		return "Connection timed out."
	except requests.exceptions.ConnectionError:
		return "Could not connect to server."
	except requests.exceptions.ReadTimeout:
		return "Server took too long to send results."
	try:
		user.raise_for_status()
	except requests.exceptions.HTTPError as e:
		return "HTTP error: " + e.message
	try:
		uData = user.json()
	except ValueError:
		return user.content
	try:
		uEntry = uData['data'][0]
	except IndexError:
		return "No results found."
	uid = uEntry['id']
	slug = uEntry['attributes']['slug']
	userName = uEntry['attributes']['name']
##	waifu logic
	waifuOrHusbando = uEntry['attributes'].get('waifuOrHusbando')
	if waifuOrHusbando:
		waifu = uData['included'][0]['attributes'].get('canonicalName')
	else:
		waifu = 'Not set!'
##	stats logic
	statsLink = api + 'users/' + uid + sFilter
	stats = requests.get(statsLink)
	try:
		sData = stats.json()
	except ValueError:
		return stats.content
	try:
		sEntry = sData['data'][0]
		lwoa = sEntry['attributes']['statsData'].get('time')
##	library logic
		libraryLink = api + 'users/' + uid + lFilter
		library = requests.get(libraryLink)
		lData = library.json()
		l0Name = lData['included'][0]['attributes'].get('canonicalTitle',None)
		if l0Name:
			l0Prog = lData['data'][0]['attributes'].get('progress')
			slug += '. Last Updated: {l0Name} to {l0Prog}'.format(l0Name=l0Name, l0Prog=l0Prog)
		l1Name = lData['included'][1]['attributes'].get('canonicalTitle',None)
		if l1Name:
			l1Prog = lData['data'][1]['attributes'].get('progress')
			slug += ', {l1Name} to {l1Prog}'.format(l1Name=l1Name, l1Prog=l1Prog)
		l2Name = lData['included'][2]['attributes'].get('canonicalTitle',None)
		if l2Name:
			l2Prog = lData['data'][2]['attributes'].get('progress')
			slug += ', {l2Name} to {l2Prog}'.format(l2Name=l2Name, l2Prog=l2Prog)
	except IndexError:
		return "No stats found for this user."
##	user search results output
	return "{userName}'s {waifuOrHusbando} is {waifu}, and they have wasted {lwoa} minutes of their life on Japanese cartoons. Tell {userName} how much of a weeb they are at https://kitsu.io/users/{slug}".format(userName=userName, waifuOrHusbando=waifuOrHusbando.lower(), waifu=waifu, lwoa=lwoa, slug=slug)
##	character lookup
@commands('kc')
@example('.kc Son Goku')
def kc(bot, trigger):
	query = trigger.group(2) or ''
	query = slugify(query)
	bot.say("%s" % fetch_character(query))
##	character search query
def fetch_character(query):
	if not query:
		return "No search query provided."
	try:
		character = requests.get(api + cFilter % query, timeout=(10.0, 4.0))
	except requests.exceptions.ConnectTimeout:
		return "Connection timed out."
	except requests.exceptions.ConnectionError:
		return "Could not connect to server."
	except requests.exceptions.ReadTimeout:
		return "Server took too long to reply."
	try:
		character.raise_for_status()
	except requests.exceptions.HTTPError as e:
		return "HTTP error: " + e.message
	try:
		Data = character.json()
	except ValueError:
		return character.content
	try:
		Entry = Data['data'][0]
		name = Entry['attributes'].get('name')
		description = web.decode(bleach.clean(Entry['attributes'].get('description')[:250].replace('<br/>', ' '), strip=True))
	except IndexError:
		return "No results found."
##	character search results output
	return "{name} - Description: {description}...".format(name=name, description=description)
