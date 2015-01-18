
#more info http://rdflib.readthedocs.org/en/latest/intro_to_creating_rdf.html

from rdflib import Namespace, Literal, URIRef, Graph
import csv, json



names = Graph()


#matt: we don't need this anymore right?

# no_dupes_index = {}

# with open('tulane-no-dupes.csv', 'r') as csvfile:

# 	#dumps the file into the cvs library with some info on how it is formated
# 	no_dupes = csv.reader(csvfile, delimiter=',')
	
# 	for row in no_dupes:
		
# 		no_dupes_full_name = row[0]
# 		no_dupes_id = row[5]

# 		no_dupes_index[no_dupes_id] = no_dupes_full_name

# print (no_dupes_index)






#set up the photo dictionary
photo_dict = {}

#set up the location dictionary
photo_place = {}

#set up the date dictionary
photo_date = {}

with open('data/tulane-refined.csv', 'r') as csvfile2:

	#dumps the file into the cvs library with some info on how it is formatted
	tulane_refined = csv.reader(csvfile2, delimiter=',')
				
	for row in tulane_refined:
					
		full_name = row[4]
		photoURL = row[39]
		placeURI = row[43]
		date = row[11]

		#look for the photoURL in the dictionary; if it's already there, add the Tulane name to the value array
		if photoURL in photo_dict: 
			photo_dict[photoURL].append(full_name)

		#else create a new key:[value] pair
		else:
			photo_dict[photoURL] = [full_name]

#print (photo_dict)
#print ("we have", len(photo_dict), "photos and", sum(len(v) for v in photo_dict.items()), "depictions")

		#if there's a place URI, put it in the dictionary with the photoURL as key
		if placeURI:
			photo_place[photoURL] = placeURI

		if date:
			photo_date[photoURL] = date


#matt: we are going to do something similar as the photo_dict here but use the peoples URIs as the values instead of the tulane names
#so it will be something like 
#{ "http://cdm16313.contentdm.oclc.org:80/cdm/ref/collection/p16313coll33/id/4" : [URI_1,URI_2,URI_3] }
knows_of_dict = {}


#now let's create some triples
with open('data/tulane_results.json') as viaf_matches_data:    
    viaf_matches = json.load(viaf_matches_data)


for a_match in viaf_matches:

	#print (viaf_matches[a_match]['tulane_last'])

	if viaf_matches[a_match]['mapping_quality'] == 'high':


		mappings = viaf_matches[a_match]['mapping'][0]


		lc_source = None
		wkp_source = None

		#matt: added this so the check works below, otherwise it would reuse the variable in the loop, we need to reset it each itteration of the loop
		subject = None

		for a_source in mappings['sources']:

			if a_source.find('WKP|') > -1:
				wkp_source = a_source.split("|")[1]

			if a_source.find('LC|') > -1:
				lc_source = a_source.split("|")[1]

		if wkp_source != None:
			subject = URIRef("http://dbpedia.org/resource/" + wkp_source.replace('"','%22'))
		elif lc_source != None:
			subject = URIRef("http://id.loc.gov/authorities/names/" + lc_source.replace(' ',''))
		else:
			#use_source = mappings['sources'][0].split("|")[1]
			print (viaf_matches[a_match]['tulane_name'], "Non-Wiki or LC auth!", mappings['sources'])


		if subject:

			names.add((subject, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")  ,URIRef("http://xmlns.com/foaf/0.1/Person")))
			names.add((subject, URIRef("http://xmlns.com/foaf/0.1/name")  , Literal(viaf_matches[a_match]['tulane_name'], lang='en')  ))

			for key, value in photo_dict.items():

				if viaf_matches[a_match]['tulane_name'] in value:

					names.add((subject, URIRef("http://xmlns.com/foaf/0.1/depiction")  , URIRef(key) ))

					#matt:
					#does this photo key exist in the dict for the knowsof, otherwise make it and add in this person's uri
					if key in knows_of_dict: 

						#make sure it is not already in there
						if subject not in knows_of_dict[key]:
							knows_of_dict[key].append(subject)

					#else create a new key:[value] pair
					else:
						knows_of_dict[key] = [subject]

					#does this photo have a placeURI in the photo_place dict?
					if key in photo_place:
						names.add(( URIRef(key), URIRef("http://purl.org/dc/terms/spatial"), URIRef(photo_place[key]) ))

					#does this photo have a date in the date dict?
					if key in photo_date:
						names.add(( URIRef(key), URIRef("http://purl.org/dc/terms/created"), Literal(photo_date[key]) ))


#matt: now we have a dict of photo urls that have the uris that appear in them, so we can say they know each other 
for a_uri in knows_of_dict:

	#make the code a little more readable
	photoURL = a_uri
	people_uris = knows_of_dict[a_uri]

	#loop through the URIs (if it is greater than 1 person)
	if len(people_uris) > 1:


		#loop through all the people

		for person_x in people_uris:

			#now loop though it again to get the others
			for person_y in people_uris:

				#we are not ourselves 
				if person_x != person_y:

					#print (person_x, "knows", person_y)

					#Build this triple and add it to the names graph
					names.add((person_x, URIRef("http://xmlns.com/foaf/0.1/knows"), person_y))
	





# Example, of how the dict would look based off the large sheet.
# {
# 	"http://cdm16313.contentdm.oclc.org:80/cdm/ref/collection/p16313coll33/id/4" : ["name1","name2","name3"]
# 
# }

names.serialize("data/names.nt", format="nt")




