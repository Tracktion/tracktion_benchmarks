#!/usr/bin/python

import urllib.request, json, os, sys, time

# Parse args
if len (sys.argv) < 4:
  print ("Not enough arguments. Base ID, API Key and dest filename must be supplied")
  sys.exit (1)

BASE_ID = sys.argv[1]
API_KEY = sys.argv[2]
FILE_NAME = sys.argv[3]

retries = 5
segment = 1

# Reads a segment from the API and returns it as a JSON object
def readContent (offset):
  url = "https://api.airtable.com/v0/{}/benchmarks?view=Grid%20view{}".format (BASE_ID, offset)
  request = urllib.request.Request (url, headers = { "Authorization": "Bearer {}".format (API_KEY) })
  response = urllib.request.urlopen (request);
  
  if response.status == 422 and retries > 0:
    retries -= 1
    time.sleep (30) # Wait for limits to be freed up
    return readContent (offset)

  return json.loads (response.read())

# Read the first section
print ("INFO: Reading segment {}".format (segment))
obj = readContent ("")

records = obj["records"]
offset = obj.get ("offset")

# Append any additional sections
while offset:
  segment += 1
  print ("INFO: Reading segment {}".format (segment))
  obj2 = readContent ("&offset=" + offset)
  records.extend (obj2["records"])
  offset = obj2.get ("offset")

print ("Num benchmarks: {}".format (len (records)))

if obj.get ("offset"):
  obj.pop ("offset")

# Overwrite js file with newly downloaded data
if os.path.exists (FILE_NAME):
  os.remove (FILE_NAME)

f = open (FILE_NAME, "a")
f.write ("var benchmarks = '{}'".format (json.dumps (obj)))
f.close()
