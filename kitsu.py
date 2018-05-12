from sopel.module import commands, example
import requests
api = 'https://kitsu.io/api/edge/anime?page[limit]=1&filter[text]=%s'
@commands('kitsu')
@example('.kitsu Clannad')
def kitsu(bot, trigger):
	query = trigger.group(2) or None
	bot.say("[Kitsu] %s" % fetch_result(query))
def fetch_result(query):
	if not query:
		return "No search query provided."
	try:
		r = requests.get(url=api % query, timeout=(10.0, 4.0))
	except requests.exceptions.ConnectTimeout:
		return "Connection timed out."
	except requests.exceptions.ConnectionError:
		return "Could not connect to server."
	except requests.exceptions.ReadTimeout:
		return "Server took too long to send results."
	try:
		r.raise_for_status()
	except requests.exceptions.HTTPError as e:
		return "HTTP error: " + e.message
	try:
		data = r.json()
	except ValueError:
		return r.content
	try:
		entry = data['data'][0]
	except IndexError:
		return "No results found."
	title = entry['attributes'][0].get('canonicalTitle')
	return "{title}".format(title=title)
