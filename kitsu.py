from sopel.module import commands, example
import requests
api = 'https://kitsu.io/api/edge/'
aFilter = 'anime?page[limit]=5&filter[text]=%s'
uFilter = 'users?include=waifu&fields[users]=name,waifuOrHusbando,slug&fields[characters]=canonicalName&page[limit]=1&filter[name]=%s'
sFilter = '/stats?filter[kind]=anime-amount-consumed'
lFilter = '/library-entries?page[limit]=3&sort=-progressedAt,updatedAt&include=media&fields[libraryEntries]=status,progress'
@commands('ka')
@example('.ka Clannad')
def ka(bot, trigger):
	query = trigger.group(2) or None
	bot.say("[Kitsu] %s" % fetch_anime(query))
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
		return "Server took too long to send results."
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
	enTitle = aEntry['attributes']['titles'].get('en','No English Title')
	status = aEntry['attributes'].get('status','Unknown')
	count = aEntry['attributes'].get('episodeCount','Unknown')
	date = aEntry['attributes'].get('startDate','Unknown')[:4]
	slug = aEntry['attributes'].get('slug','None')
	synopsis = aEntry['attributes'].get('synopsis','None')[:250]
	return "{title} ({enTitle}) - {status} - Episodes: {count} - Aired: {date} - https://kitsu.io/anime/{slug} - Synopsis: {synopsis}...".format(title=title, enTitle=enTitle, status=status, count=count, date=date, slug=slug, synopsis=synopsis)
@commands('ku')
def ku(bot, trigger):
	query = trigger.group(2) or None
	bot.say("[Kitsu] %s" % fetch_user(query))
def fetch_user(query):
	if not query:
		return "No search query provided."
#	user section
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
#	waifu section
	waifuOrHusbando = uEntry['attributes'].get('waifuOrHusbando')
	if waifuOrHusbando:
		waifuLink = api + 'users/' + uid + '/waifu'
		try:
			waifus = requests.get(waifuLink)
		except IndexError:
			return
		try:
			wData = waifus.json()
		except ValueError:
			return waifus.content
		try:
			wEntry = wData['data']
		except IndexError:
			return
		waifu = wEntry['attributes'].get('name')
	else:
		waifu = 'Not set!'
#	stats section
	statsLink = api + 'users/' + uid + sFilter
	try:
		stats = requests.get(statsLink)
	except IndexError:
		return
	try:
		sData = stats.json()
	except ValueError:
		return stats.content
	try:
		sEntry = sData['data'][0]
	except IndexError:
		return
	lwoa = sEntry['attributes']['statsData'].get('time')
#	library section
	libraryLink = api + 'users/' + uid + lFilter
	try:
		library = requests.get(libraryLink)
	except IndexError:
		return
	try:
		lData = library.json()
	except ValueError:
		return library.content
	a0Name = lData['included'][0]['attributes'].get('canonicalTitle','None')
	a1Name = lData['included'][1]['attributes'].get('canonicalTitle','None')
	a2Name = lData['included'][2]['attributes'].get('canonicalTitle','None')
	a0Prog = lData['data'][0]['attributes'].get('progress','None')
	a1Prog = lData['data'][1]['attributes'].get('progress','None')
	a2Prog = lData['data'][2]['attributes'].get('progress','None')
#	results output
	return "{userName} - {waifuOrHusbando}: {waifu} - Life Wasted On Anime: {lwoa} minutes - https://kitsu.io/users/{slug} - Last Updated: {a0Name} to {a0Prog}, {a1Name} to {a1Prog} and {a2Name} to {a2Prog}".format(userName=userName, waifu=waifu, slug=slug, waifuOrHusbando=waifuOrHusbando, lwoa=lwoa, uid=uid, a0Name=a0Name, a1Name=a1Name, a2Name=a2Name, a0Prog=a0Prog, a1Prog=a1Prog, a2Prog=a2Prog)
