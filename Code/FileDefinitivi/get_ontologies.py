from clean_uri import cleanUri
import urllib.request

url = "http://www.w3.org/2006/time"
filename = cleanUri(url)+".ttl"
urllib.request.urlretrieve(url, filename)
