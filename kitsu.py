##	python modules
from sopel.module import commands, example
import requests
from slugify import slugify
##
api = 'https://kitsu.io/api/edge/'
aFilter = 'anime?page[limit]=5&filter[text]=%s'
uFilter = 'users?include=waifu&fields[users]=name,waifuOrHusbando,slug&fields[characters]=canonicalName&page[limit]=1&filter[name]=%s'
sFilter = '/stats?filter[kind]=anime-amount-consumed'
lFilter = '/library-entries?page[limit]=3&sort=-progressedAt,updatedAt&include=media&fields[libraryEntries]=status,progress&fields[anime]=canonicalTitle&fields[manga]=canonicalTitle'
##	anime search trigger
@commands('ka')
@example('.ka Clannad')
def ka(bot, trigger):
	query = trigger.group(2) or None
	query = slugify(query)
	bot.say("[Kitsu] %s" % fetch_anime(query))
##	anime search query
def fetch_anime(query):
	if not query:
		return "No search query provided."
	try:
		anime = requests.get(api + aFilter % query, timeout=(10.0, 4.0))
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
		aData = anime.json()
	except ValueError:
		return anime.content
	try:
		aEntry = aData['data'][0]
	except IndexError:
		return "No results found."
	title = aEntry['attributes'].get('canonicalTitle','None')
	enTitle = aEntry['attributes']['titles'].get('en',None)
	if enTitle:
		title += ' ({enTitle})'.format(enTitle=enTitle)
	status = aEntry['attributes'].get('status','Unknown')
	subtype = aEntry['attributes'].get('subtype',None)
	count = aEntry['attributes'].get('episodeCount','Unknown')
	date = aEntry['attributes'].get('startDate','Unknown')[:4]
	slug = aEntry['attributes'].get('slug',None)
	synopsis = aEntry['attributes'].get('synopsis','None found.')[:250]
##	anime search results output
	return "[{subtype}] {title} - {status} - Episodes: {count} - Aired: {date} - https://kitsu.io/anime/{slug} - Synopsis: {synopsis}...".format(subtype=subtype, title=title, status=status, count=count, date=date, slug=slug, synopsis=synopsis)
##	user search trigger
@commands('ku')
def ku(bot, trigger):
	query = trigger.group(2) or None
	bot.say("[Kitsu] %s" % fetch_user(query))
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
	except IndexError:
		return "No library data found for this user."
	lwoa = sEntry['attributes']['statsData'].get('time')
##	library logic
	libraryLink = api + 'users/' + uid + lFilter
	library = requests.get(libraryLink)
	lData = library.json()
	l0Name = lData['included'][0]['attributes'].get('canonicalTitle',None)
	if l0Name:
		l0Prog = lData['data'][0]['attributes'].get('progress')
		slug += ' - Last Updated: {l0Name} to {l0Prog}'.format(l0Name=l0Name, l0Prog=l0Prog)
	l1Name = lData['included'][1]['attributes'].get('canonicalTitle',None)
	if l1Name:
		l1Prog = lData['data'][1]['attributes'].get('progress')
		slug += ', {l1Name} to {l1Prog}'.format(l1Name=l1Name, l1Prog=l1Prog)
	l2Name = lData['included'][2]['attributes'].get('canonicalTitle',None)
	if l2Name:
		l2Prog = lData['data'][2]['attributes'].get('progress')
		slug += ', {l2Name} to {l2Prog}'.format(l2Name=l2Name, l2Prog=l2Prog)
##	user search results output
	return "{userName} - {waifuOrHusbando}: {waifu} - Life Wasted On Anime: {lwoa} minutes - https://kitsu.io/users/{slug}".format(userName=userName, waifu=waifu, slug=slug, waifuOrHusbando=waifuOrHusbando, lwoa=lwoa, uid=uid)