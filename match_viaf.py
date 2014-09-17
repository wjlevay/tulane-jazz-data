# -*- encoding: utf-8 -*-
import time, requests, json, sys, csv
import xml.etree.ElementTree as etree 
 



class viafSearch:




	viafURL = 'http://viaf.org/viaf/search?query=local.personalNames+%3D+{SEARCH}&httpAccept=text/xml'
	sourceFile = 'data/tulane-no-dupes.csv'
	resultsFile = 'data/tulane_results.json'
	results = {}
	requestDelay = 0.1



	def __init__(self):


		self.processFile()

		self.saveFile()

		self.stats()




	def requestProcess(self,searchVal):


		
		r = requests.get(self.viafURL.replace('{SEARCH}',searchVal))

		time.sleep(self.requestDelay)

		results = []

		if (r.status_code == 200):


			try:
				root = etree.fromstring(r.text)	
			except:
				print ("Error in parsing the XML", "URL")

			for records in root.findall('{http://www.loc.gov/zing/srw/}records'):
				for record in records:


					aResult = {}
					aResult['birthDate'] = None
					aResult['deathDate'] = None
					aResult['altNames'] = []
					aResult['sources'] = []
					aResult['titles'] = []


					for recordData in record.findall('{http://www.loc.gov/zing/srw/}recordData'):


						for viafCluster in recordData.findall('{http://viaf.org/viaf/terms#}VIAFCluster'):


							for el in viafCluster.findall('{http://viaf.org/viaf/terms#}birthDate'):
								aResult['birthDate'] = el.text

							for el in viafCluster.findall('{http://viaf.org/viaf/terms#}deathDate'):
								aResult['deathDate'] = el.text

							for mainHeadings in viafCluster.findall('{http://viaf.org/viaf/terms#}mainHeadings'):
								for el in mainHeadings.findall('{http://viaf.org/viaf/terms#}data'):
									aResult['altNames'].append((el[0].text))

							for sources in viafCluster.findall('{http://viaf.org/viaf/terms#}sources'):
								for el in sources:
									aResult['sources'].append(el.text)

							for titles in viafCluster.findall('{http://viaf.org/viaf/terms#}titles'):
								for el in titles:

									#they are contained in a sub work element that has a source and title
									for workPart in el:

										#is this the title element?
										if (workPart.tag == '{http://viaf.org/viaf/terms#}title'):
											aResult['titles'] .append(workPart.text)


					results.append(aResult)

			return results						

		else:


			print ("Error in requesting", "URL")

			return []


	def processFile(self):

		counter = 0

		with open(self.sourceFile, 'r') as csvfile:

			#dumps the file into the csv library with some info on how it is formatted
			persons = csv.reader(csvfile, delimiter=',')
			
			for row in persons:
				
				fullName = row[0]
				firstName = row[1]
				lastName = row[2]
				dobYear = row[3]
				dodYear = row[4]


				self.results[fullName]  = {}

				self.results[fullName]['tulane_name'] = fullName
				self.results[fullName]['tulane_first'] = firstName
				self.results[fullName]['tulane_last'] = lastName
				self.results[fullName]['tulane_dob'] = dobYear
				self.results[fullName]['tulane_dod'] = dodYear
				self.results[fullName]['mapping'] = []

				#here is a line of data from tulane


				counter = counter + 1
				print ("On ", counter)

				self.processPerson(fullName)


				#save
				if counter % 25 == 0:
					self.saveFile()


	def processPerson(self,fullName):


		print (self.results[fullName]['tulane_name'])

		searchResult = []


		searchString = self.results[fullName]['tulane_name']

		if (self.results[fullName]['tulane_dob'] != 'NULL'):

			searchString += " " + self.results[fullName]['tulane_dob']

			#search with the DOB one way
			searchResult = self.requestProcess(searchString)

			print ("\t",searchString,"Found:",len(searchResult))

			if (len(searchResult) == 0):

				#try another format that VIAF search engine seems to like sometimes
				searchString = self.results[fullName]['tulane_name'] + "," + self.results[fullName]['tulane_dob']

				print ("\t",searchString,"Found:",len(searchResult))


		#if no luck with that try regular name search
		if (len(searchResult) == 0):

			searchString = self.results[fullName]['tulane_name']
			searchResult = self.requestProcess(searchString)

			print ("\t",searchString,"Found:",len(searchResult))

		quality = "low"

		#lets qualify a little bit
		if(self.results[fullName]['tulane_dob'] != 'NULL' and len(searchResult) == 1):
			quality = 'high'

		if(self.results[fullName]['tulane_dob'] == 'NULL' and len(searchResult) == 1):
			quality = 'medium'



		if(len(searchResult) > 1):
			#Bill's attempt to find whitelisted terms in the "titles" field 

			#set up a whitelist of terms
			terms = ['jazz', 'new orleans', 'ragtime', 'gospel', 'blues',]

			#set up the new whitelist results list
			whitelistResult = []

			for aResult in searchResult:


				titles = aResult['titles']
				names = aResult['altNames']

				#titles is an array, loop through it
				for aTitle in titles:


					#check if there's a whitelisted term in the "titles" results
					for term in terms:
						if (aTitle.lower().find(term) != -1):
							
							#check if the names match at least a little
							#if self.results[fullName]['tulane_last'] in names:

							#then add the result to the new list if it's not already there
							if aResult not in whitelistResult:
								whitelistResult.append(aResult)




			#if our new results list has one or more results, replace the original searchResult
			if(len(whitelistResult) > 0):
				searchResult = whitelistResult
				

			#after all that if we narrowed it down to a single person set it to high probability
			if(len(searchResult) == 1):

				print ("THE WHITELIST WORKED ON THIS ONE!!!")
				print (searchResult)
				print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				quality = 'high'


		if(len(searchResult) == 0):
			quality = 'none'

		if(len(searchResult) == 100):
			searchResult = []
			quality = 'manual'




		self.results[fullName]['mapping'] = searchResult
		self.results[fullName]['mapping_quality'] = quality

		#safe it after each try, just to see the progress and not have to wait till the end to check it
		self.saveFile()



	def saveFile(self):
		f = open(self.resultsFile, "w")
		f.write(json.dumps(self.results, indent=4, sort_keys=True))



	def stats(self):


		matchTypes = {}
		manyMatchCount = {}

		with open(self.resultsFile, 'r') as jsonFile:


			results = json.loads(jsonFile.read())

			for aResult in results:

				x =  results[aResult]

				if x['mapping_quality'] not in matchTypes:
					matchTypes[x['mapping_quality']] = 1
				else:
					matchTypes[x['mapping_quality']] += 1


				if x['mapping_quality'] == 'many':

					if len(x['mapping']) not in manyMatchCount:
						manyMatchCount[len(x['mapping'])] = 1
					else:
						manyMatchCount[len(x['mapping'])] += 1



		print (matchTypes)

		for x in manyMatchCount:
			print (x,"|",manyMatchCount[x])



if __name__ == "__main__":

	v = viafSearch()
