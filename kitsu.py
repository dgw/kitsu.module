from sopel.module import commands, example
import requests
api = 'https://kitsu.io/api/edge/'
aFilter = 'anime?page[limit]=5&filter[text]='
@commands('kitsu')
@example('.kitsu Clannad')
def kitsu(bot, trigger):
	query = trigger.group(2) or None
	bot.say("[Kitsu] " + fetch_result(query))
def fetch_result(query):
	if not query:
		return "No search query provided."
	try:
		call = requests.get(api + aFilter + query, timeout=(10.0, 4.0))
	except requests.exceptions.ConnectTimeout:
		return "Connection timed out."
	except requests.exceptions.ConnectionError:
		return "Could not connect to Kitsu."
	except requests.exceptions.ReadTimeout:
		return "Kitsu took too long to return results."
	try:
		call.raise_for_status()
	except requests.exceptions.HTTPError as e:
		return "HTTP error: " + e.message
	try:
		data = call.json()
	except ValueError:
		return call.content
	try:
		entry = data['data'][0]
	except IndexError:
		return "No results found."
	title = entry['attributes'][0].get('canonicalTitle')
	return "{title}".format(title=title)
