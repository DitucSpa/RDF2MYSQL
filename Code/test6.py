# pip install python-magic-bin==0.4.14
import magic

print(magic.from_file('jsonld.owl'))

# printing the mime type of the file
print(magic.from_file('jsonld.owl', mime = True))
