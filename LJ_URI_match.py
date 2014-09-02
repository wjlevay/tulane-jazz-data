#import a non-built in library to help us word with RDF graphs. 
#rdflib and isodate (used by rdflib) are python libraries writen by someone else (https://github.com/RDFLib/rdflib)
#the correct way to do this would be to install the libraries system wide by typing "easy_install rdflib" or "pip install rdflib" at the command line
#but I'm including them here in the folder just to make it easier to get started
import rdflib
import sys

#first we want to open the linked jazz  directory and load all the names into a dictonary

#define the variable g as a RDF Graph
g = rdflib.Graph()


#tell it to open the linkedjazz.nt file in the data folder
g.parse("data/linkedjazz.nt", format="nt")

#an array where we will keep the linked jazz URIs
linkedJazzNames = []

for subj, pred, obj in g:

	#this print statement would print the subject predicate and object of each triple
	#print subj,pred,obj

	#but we just care about the URIs, the rdflib.URIRef() bit is just using the library's data type of URI, so its asking if the two URIs match
	#another way you could do this would be:
	#if str(pred) == "http://xmlns.com/foaf/0.1/name":
	#this is converting the predicate to a string value and comparing it vs another string.	
	if pred == rdflib.URIRef("http://xmlns.com/foaf/0.1/name"):
		
		#print sub
		#add the name to our array
		linkedJazzNames.append(subj)


#we have the URIs loaded, how many?
print "We have", len(linkedJazzNames), "URIs from linkedjazz.nt!"


#next we want to open the Tulane triplestore and load all the names into a dictonary

#define the variable h as a RDF Graph
h = rdflib.Graph()


#tell it to open the names.nt file in the data folder
h.parse("data/names.nt", format="nt")

#an array where we will keep the Tulane names
tulaneNames = []

for subj, pred, obj in h:

	if pred == rdflib.URIRef("http://xmlns.com/foaf/0.1/name"):
		
		tulaneNames.append(subj)


#we have the URIs loaded, how many?
print "We have", len(tulaneNames), "URIs from Tulane!"

#let's match these URIs!
matches = []
non_matches = []

for aLJName in linkedJazzNames:

	for aTName in tulaneNames:

		if aLJName == aTName:

			matches.append(aLJName)

			print aLJName, "is a match!"

for aTName in tulaneNames:

	if aTName not in matches:

		non_matches.append(aTName)

		print aTName, "is NOT a match!"

print len(matches), "matches"
print len(non_matches), "non-matches"


sys.exit()





