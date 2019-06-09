import sys
import csv
import yaml
import vobject
import database as db
import mysql.connector
from mysql.connector import errorcode

def format_header(print_flag):
	""" prints header
	"""

	# additional settings
	lastname_ljust = 20
	firstname_ljust = 20
	mobile_ljust = 15
	affiliation_ljust = 15

	# w/ affiliation
	if print_flag == 1:
		header = "\n{} {} {} {}".format("First Name".ljust(firstname_ljust), "Last Name".ljust(lastname_ljust), "Mobile".ljust(mobile_ljust), "Affiliation".ljust(affiliation_ljust))
	# w/o affiliation
	elif print_flag == 2:
		header = "\n{} {} {}".format("First Name".ljust(firstname_ljust), "Last Name".ljust(lastname_ljust), "Mobile".ljust(mobile_ljust))
	# No other case should be found
	else:
		raise ValueError("Error in flag settings value: Value {} was found".format(print_flag))
		
	print(header)
	print('-' * len(header))

def format_line(line, print_flag):
	''' formats line for printing
	'''

	# additional settings
	lastname_ljust = 20
	firstname_ljust = 20
	mobile_ljust = 15
	affiliation_ljust = 15

	firstname = line[0].ljust(firstname_ljust)
	lastname = line[1].ljust(lastname_ljust)
	mobile = line[2].ljust(mobile_ljust)

	# w/ affiliation
	if print_flag == 1:
		affiliation = line[3].ljust(mobile_ljust)
		print("{} {} {} {}".format(firstname, lastname, mobile, affiliation))
	# w/o affiliation
	elif print_flag == 2:
		print("{} {} {}".format(firstname, lastname, mobile))
	# No other case should be found
	else:
		raise ValueError("Error in flag settings value: Value {} was found".format(print_flag))

def print_entire_library():
	people = db.getAllPeople(conn)
	if len(people) == 0:
		print("No people exist.")
		return
	
	format_header(1)
	peepLen = range(len(people))
	for i in peepLen:
		format_line(people[i], 1)
	
def search_by_affilation():
	affiliations = db.getAllAffiliations(conn)
	if len(affiliations) == 0:
		print("No affiliations exist.")
		return
	
	# Prints list of affiliations
	affLen = range(len(affiliations))
	print()
	for i in affLen:
		print("(" + str(i + 1) + ") " + affiliations[i][0])
	print()
	
	# Returns user-selected affiliation
	while True:
		choice = int(input("Select the affiliation you wish to search for: "))
		if (choice - 1) in affLen:
			affiliation = affiliations[choice - 1][0]
			break
		else:
			print('Invalid choice. Please try again.')

	aid = db.getAffiliationId(conn, affiliation)
	people = db.getPeopleFromAid(conn, aid)
	
	format_header(2)
	peepLen = range(len(people))
	for i in peepLen:
		format_line(people[i], 2)
	
def create_entry(first, last, mobile, affiliation):

	# scrub mobile input
	if mobile[:2] == "+1":
		mobile = mobile[2:]
	if ("(" or ")" or "-") not in mobile:
		mobile = "(" + mobile[0:3] + ")" + mobile[3:6] + "-" + mobile[6:]
	
	# check for first time occurence of affilation
	aid = db.getAffiliationId(conn, affiliation)
	if not aid:
		db.addAffiliation(conn, affiliation)
		aid = db.getAffiliationId(conn, affiliation)
		
	try:
		db.addPerson(conn, first, last, mobile, aid)
	except Exception as e:
		print("Error inserting into database: {}".format(e))
		
def delete_entry():
	person = input('Please enter the name of the person you wish to delete (type "all" for all: ')
	
	# delete all or get uid of specified user
	if person == "all":
		db.deleteAll(conn)
		return
	else:
		uid = db.getPersonID(conn, person)
	
	# person not found in database
	if uid == -1:
		print("Person not found in database")
	# multiple people found with search terms
	elif uid == -2:
		print("Multiple people found with search term. Please be more specific.")
	else:
		aid = db.getPersonAffiliation(conn, uid)
		try:
			db.deletePerson(conn, uid)
		except Exception as e:
			print("Error deleting from database: {}".format(e))
		else:
			print("Person {} deleted from database".format(person))
			
		# check if affilation is defunct
		people = db.getPeopleFromAid(conn, aid)
		if people == []:
			db.deleteAffiliation(conn, aid)
			print("Affiliation {} deleted from database".format(aid))
		
def import_csv():
	filename = input("Please input CSV file name to export to (will be in current directory): ")
	try:
		with open(filename, "r") as csv_file:
			for line in csv_file:
				line = line[:-1]
				line = line.split(',')
				
				# remove apostrophes from fields as they cause issues with SQL
				first = line[0].replace("'","")
				last = line[1].replace("'","")
				mobile = line[2].replace("'","")
				affiliation = line[3].replace("'","")
				
				create_entry(first, last, mobile, affiliation)
				
	except Exception as e:
		print("Error processing CSV file: {}".format(e))
		
	else:
		print("Import Complete")

def export_csv():
	filename = input("Please input CSV file name to export to (will be in current directory): ")
	
	# append file extension if not included
	print(filename[-4:])
	if filename[-4:] != ".csv":
		filename += ".csv"
	
	try:
		with open(filename, "w") as csv_file:
			people = db.getAllPeople(conn)
			people_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for person in people:
				people_writer.writerow([person[1], person[0], person[2], person[3]])
				
	except Exception as e:
		print("Error processing CSV file: {}".format(e))
		
	else:
		print("Export Complete")

def import_vcf():
	filename = input("Please input VCF file name to import from (must be in current directory): ")
	try:
		with open(filename, "r") as vcf_file:
			for entry in vobject.readComponents(vcf_file):
				name = entry.fn.value
				name = name.split(" ")
				if len(name) == 2:
					first = name[0]
					last = name[1]
				else:
					first = name[0]
					last = None
				mobile = entry.tel.value
				affiliation = None
				create_entry(first, last, mobile, affiliation)
				
	except Exception as e:
		print("Error processing VCF file: {}".format(e))

	else:
		print("Import Complete")
		
def export_vcf():
	filename = input("Please input VCF file name to export to (will be in current directory): ")
	
	# append file extension if not included
	print(filename[-4:])
	if filename[-4:] != ".vcf":
		filename += ".vcf"
	
	try:
		with open(filename, "a") as vcf_file:
			people = db.getAllPeople(conn)
			for person in people:
				new_person = vobject.vCard()
				new_person.add('fn')
				new_person.fn.value = person[1] + " " + person[0]
				new_person.add('tel')
				new_person.tel.value = person[2]
				new_person.add('org')
				new_person.org.value = [person[3]]
				new_person.serialize()
				vcf_file.write(str(new_person) + "\n")
				
	except Exception as e:
		print("Error processing VCF file: {}".format(e))
		
	else:
		print("Export Complete")

def main():
	while True:
		print("\n-------------\n     ACE     \n-------------")
		print("(1) Show entire library")
		print("(2) Find affiliation")
		print("(3) Write a new entry")
		print("(4) Delete an entry")
		print("(5) Source from CSV")
		print("(6) Source from VCF")
		print("(7) Export to CSV")
		print("(8) Export to VCF")
		print("(0) Exit Program\n")
		
		choice = input("Make a selection: ")

		# ensure choice is type int
		try:
			choice = int(choice)
		except ValueError:
			print("\nPlease input a number.")
		else:

			# CLI Formatting
			print()

			# print whole library
			if choice == 1:
				print_entire_library()
			
			# sort by avaliable affliations
			elif choice == 2:
				search_by_affilation()
			
			# write new entry
			elif choice == 3:
				first = input("Please enter first name: ")
				last = input("Please enter last name: ")
				mobile = input("Please enter mobile number: ")
				affiliation = input("Please enter affiliation: ")
				create_entry(first, last, mobile, affiliation)
			
			# delete entry
			elif choice == 4:
				delete_entry()

			# source from csv
			elif choice == 5:
				print("NOTE: CSV must be in format <first_name>,<last_name>,<mobile>,<affiliation>")
				import_csv()

			# source from vcf
			elif choice == 6:
				import_vcf()

			# export to csv
			elif choice == 7:
				print("NOTE: CSV will be in format <first_name>,<last_name>,<mobile>,<affiliation>")
				export_csv()

			# export to vcf
			elif choice == 8:
				export_vcf()

			# exit
			elif choice == 0:
				break
			
			# invalid choice
			else:
				print('\nInvalid choice. Please try again.')

	print("Goodbye!\n")
	conn.close()
	sys.exit()

if __name__ == "__main__":
	if len(sys.argv) == 1:
		conf = "config.yaml"
	elif len(sys.argv) == 2:
		conf = sys.argv[1]
	else:
		print("Improper number of arguments - please see README")
		sys.exit()
		
	# load configuration data
	try:
		with open(conf, 'r') as file:
			config = yaml.load(file)
	except Exception as e:
		print("Error loading configuration data: ", e)
		sys.exit()

	# connect to database
	try:
		conn = mysql.connector.connect(user=config['mysql']['user'],
									   password=config['mysql']['password'],
									   host=config['mysql']['host'],
									   database=config['mysql']['database'])
									 
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Something is wrong with your user name or password")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database does not exist")
		else:
			print(err)
	
	else:
		main()
