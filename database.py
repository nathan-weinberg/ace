def getAllPeople(conn):
	''' gets all people
	'''
	cursor = conn.cursor()
	cursor.execute("SELECT people.first_name, people.last_name, people.phone_number, affiliations.affiliation FROM people, affiliations WHERE people.affiliated_with = affiliations.aid ORDER BY people.last_name")
	people = cursor.fetchall()
	cursor.close()
	return people

def getAllAffiliations(conn):
	''' gets all affiliation names
	'''
	cursor = conn.cursor()
	cursor.execute("SELECT affiliation FROM affiliations ORDER BY affiliation")
	affiliations = cursor.fetchall()
	cursor.close()
	return affiliations
	
def getPersonID(conn, name):
	''' takes in first and/or last name
		returns uid if one person found
		returns  -1 if no person found
		returns  -2 if multiple people found
	'''
	cursor = conn.cursor(buffered=True)
	if ' ' in name:
		name = name.split(' ')
		first = name[0]
		last = name[1]
		cursor.execute("SELECT uid FROM people WHERE first_name = '{0}' AND last_name = '{1}'".format(first, last))
		uid = cursor.fetchall()
	else:
		cursor.execute("SELECT uid FROM people WHERE first_name = '{0}' OR last_name = '{0}'".format(name))
		uid = cursor.fetchall()
	cursor.close()
	
	if len(uid) == 1:
		return uid[0][0]
	elif uid == []:
		return -1
	else:
		return -2

def getAffiliationId(conn, affiliation):
	''' gets affiliation id from affiliation name
		returns false if none found
	'''
	cursor = conn.cursor(buffered=True)
	cursor.execute("SELECT aid FROM affiliations WHERE affiliation = '{}'".format(affiliation))
	aid = cursor.fetchone()
	cursor.close()
	if aid == None:
		return False
	else:
		return aid[0]

def getAffiliationName(conn, aid):
	''' gets affiliation name from affiliation aid
		returns false if none found
	'''
	cursor = conn.cursor()
	cursor.execute("SELECT affiliation FROM affiliations WHERE aid = {}".format(aid))
	affName = cursor.fetchone()
	cursor.close()
	if affName == None:
		return False
	else:
		return affName[0]

def getPeopleFromAid(conn, aid):
	''' gets all people associated with given aid
	'''
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name, phone_number FROM people WHERE affiliated_with = '{}' ORDER BY last_name".format(aid))
	people = cursor.fetchall()
	cursor.close()
	return people
	
def addPerson(conn, first_name, last_name, phone_number, aid=None):
	''' adds Person with or without affiliation
	'''
	cursor = conn.cursor()
	if aid == None:
		cursor.execute("INSERT INTO people(first_name, last_name, phone_number) VALUES ('{}', '{}', '{}')".format(first_name, last_name, phone_number))
	else:	
		cursor.execute("INSERT INTO people(first_name, last_name, phone_number, affiliated_with) VALUES ('{}', '{}', '{}', {})".format(first_name, last_name, phone_number, aid))
		
	conn.commit()
	cursor.close()

def deletePerson(conn, uid):
	''' deletes person assoicated with given uid
	'''
	cursor = conn.cursor()
	cursor.execute("DELETE FROM people WHERE uid = {}".format(uid))
	conn.commit()
	cursor.close()
	
def deleteAllPeople(conn):
	''' deletes all people from database
	'''
	cursor = conn.cursor()
	cursor.execute("DELETE FROM people")
	conn.commit()
	cursor.close()

def addAffiliation(conn, affiliation):
	''' add Affiliation
	'''
	cursor = conn.cursor()
	cursor.execute("INSERT INTO affiliations(affiliation) VALUES ('{}')".format(affiliation))
	conn.commit()
	cursor.close()

def deleteAffiliation(conn, aid):
	''' delete affiliation associated with given aid
	'''
	cursor = conn.cursor()
	cursor.execute("DELETE FROM affiliations WHERE aid = {}".format(aid))
	conn.commit()
	cursor.close()

def deleteAllAffiliations(conn):
	''' deletes all affiliations from database
	'''
	cursor = conn.cursor()
	cursor.execute("DELETE FROM affiliations")
	conn.commit()
	cursor.close()

def getPersonAffiliation(conn, uid):
	''' gets aid of person with given uid
	'''
	cursor = conn.cursor(buffered=True)
	cursor.execute("SELECT affiliated_with FROM people WHERE uid = {}".format(uid))
	aid = cursor.fetchone()[0]
	cursor.close()
	return aid

def changePersonAffiliation(conn, uid, aid):
	''' change aid of person with given uid
	'''
	cursor = conn.cursor()
	cursor.execute("UPDATE people SET affiliated_with = {} WHERE uid = {}".format(aid, uid))
	conn.commit()
	cursor.close()
