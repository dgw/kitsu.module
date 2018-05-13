from sopel.module import commands, example
from sopel import web
import requests
api = 'https://kitsu.io/api/edge/'
aFilter = 'anime?page[limit]=5&filter[text]=%s'
uFilter = 'users?include=waifu&page[limit]=1&filter[name]=%s'
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
		anime = requests.get(api + aFilter % web.quote(query), timeout=(10.0, 4.0))
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
#	if data['meta']['count'] = 0:
#		return "No results found."
	try:
		aEntry = aData['data'][0]
	except IndexError:
		return "No results found."
	title = aEntry['attributes'].get('canonicalTitle', 'Unknown')
	enTitle = aEntry['attributes']['titles'].get('en', 'Unknown')
	status = aEntry['attributes'].get('status', 'Unknown')
	count = aEntry['attributes'].get('episodeCount', 'Unknown')
	date = aEntry['attributes'].get('startDate', 'None')[:4]
	slug = aEntry['attributes'].get('slug', 'Unknown')
	synopsis = aEntry['attributes'].get('synopsis', 'Unknown')[:250]
	return "{title} ({enTitle}) - {status} - {count} Episodes - Aired: {date} - https://kitsu.io/anime/{slug} - Synopsis: {synopsis}...".format(title=title, enTitle=enTitle, status=status, count=count, date=date, slug=slug, synopsis=synopsis)
@commands('ka')
def ku(bot, trigger):
	query = trigger.group(2) or None
	bot.say("[Kitsu] %s" % fetch_user(query))
def fetch_user(query):
	if not query:
		return "No search query provided."
	try:
		user = requests.get(api + uFilter % web.quote(query), timeout=(10.0, 4.0))
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
#	if data['meta']['count'] = 0:
#		return "No results found."
	try:
		uEntry = uData['data'][0]
	except IndexError:
		return "No results found."
	uid = uEntry['id']
	userName = uEntry['attributes'].get('name', 'Unknown')
	waifuLink = api + 'users/' + uid + '/waifu'
	statsLink = api + 'users/' + uid + sFilter
	libraryLink = api + 'users/' + uid + lFilter
	try:
		stats = requests.get(statsLink)
	except IndexError:
		return "No stats found."
	try:
		sData = stats.json()
	except ValueError:
		return stats.content
	try:
		sEntry = sData['data'][0]
	except IndexError:
		return "No stats found."
	lwoa = sEntry['attributes']['statsData'].get('time', 'None!')
	try:
		library = requests.get(libraryLink)
	except IndexError:
		return "No libraries found."
	try:
		lData = library.json()
	except ValueError:
		return library.content
	a0Name = lData['included'][0]['attributes'].get('canonicalTitle', 'None!')
	a1Name = lData['included'][1]['attributes'].get('canonicalTitle', 'None!')
	a2Name = lData['included'][2]['attributes'].get('canonicalTitle', 'None!')
	a0Prog = lData['data'][0]['attributes'].get('progress', 'None!')
	a1Prog = lData['data'][1]['attributes'].get('progress', 'None!')
	a2Prog = lData['data'][2]['attributes'].get('progress', 'None!')
	try:
		waifus = requests.get(waifuLink)
	except IndexError:
		return "No waifus found."
	try:
		wData = waifus.json()
	except ValueError:
		return waifus.content
	try:
		wEntry = wData['data']
	except IndexError:
		return "No waifus found."
	waifu = wEntry['attributes'].get('name', 'None Set!')
	return "{userName} - Waifu: {waifu} - Life Wasted On Anime: {lwoa} minutes - https://kitsu.io/users/{uid} - Last Updated: {a0Name} to {a0Prog}, {a1Name} to {a1Prog} and {a2Name} to {a2Prog}".format(userName=userName, waifu=waifu, lwoa=lwoa, uid=uid, a0Name=a0Name, a1Name=a1Name, a2Name=a2Name, a0Prog=a0Prog, a1Prog=a1Prog, a2Prog=a2Prog)
