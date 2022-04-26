def cleanUri(uri):
    uri = uri.split("/")[-1]
    if "#" in uri:
        uri = uri.split("#")[-1]
    return uri
