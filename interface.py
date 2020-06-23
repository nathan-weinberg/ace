#!/usr/bin/python3

'''
Archived Contact Engine
Copyright (C) 2020 Nathan Weinberg
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import csv
import yaml
import vobject
import argparse
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
	return None

def format_line(line, print_flag):
	""" formats and prints line
	"""

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
	return None

def print_entire_library():
	""" prints entire library
	"""

	people = db.getAllPeople(conn)
	if len(people) == 0:
		print("No people exist.")
		return None

	# print block
	format_header(1)
	peepLen = len(people)
	for i in range(peepLen):
		format_line(people[i], 1)
	print("\n{} entries".format(peepLen))
	return None

def search_by_affilation():
	""" prints users associated with particular affiliation
	"""

	affiliations = db.getAllAffiliations(conn)
	if len(affiliations) == 0:
		print("No affiliations exist.")
		return None

	# Prints list of affiliations
	affLen = range(len(affiliations))
	for i in affLen:
		print("(" + str(i + 1) + ") " + affiliations[i][0])
	print()

	# Returns user-selected affiliation
	while True:
		try:
			choice = int(input("Select the affiliation you wish to search for: "))
			if (choice - 1) in affLen:
				affiliation = affiliations[choice - 1][0]
				break
			else:
				print('Invalid choice. Please try again.')
		except KeyboardInterrupt:
			print()
			return None
		except ValueError:
			print('Invalid input. Please try again.')

	# get relevant data from database
	aid = db.getAffiliationId(conn, affiliation)
	people = db.getPeopleFromAid(conn, aid)

	# print block
	format_header(2)
	peepLen = len(people)
	for i in range(peepLen):
		format_line(people[i], 2)
	print("\n{} entries".format(peepLen))
	return None

def create_entry(first, last, mobile, affiliation):
	""" manual entry creation
	"""

	# remove apostrophes from fields as they cause issues with SQL
	first = first.replace("'","")
	last = last.replace("'","")
	mobile = mobile.replace("'","")
	affiliation = affiliation.replace("'","")

	# further scrub mobile input
	if mobile[:2] == "+1":
		mobile = mobile[2:]
	if ("(" or ")" or "-") not in mobile:
		mobile = "(" + mobile[0:3] + ")" + mobile[3:6] + "-" + mobile[6:]

	# check for first time occurrence of affiliation
	aid = db.getAffiliationId(conn, affiliation)
	if not aid:
		db.addAffiliation(conn, affiliation)
		aid = db.getAffiliationId(conn, affiliation)

	try:
		db.addPerson(conn, first, last, mobile, aid)
	except Exception as e:
		print("Error inserting into database: {}".format(e))
	else:
		print("Person {} {} added to database".format(first, last))
	return None

def delete_entry(person):
	""" manual entry deletion
	"""

	# immediately exit if no people exist in db
	people = db.getAllPeople(conn)
	if len(people) == 0:
		print("No people exist.")
		return None

	# delete all or get uid of specified user
	if person == "all":
		db.deleteAllPeople(conn)
		db.deleteAllAffiliations(conn)
		print("All entries deleted from database")
		return None
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

		# check if affiliation is defunct
		people = db.getPeopleFromAid(conn, aid)
		if people == []:
			affName = db.getAffiliationName(conn, aid)
			db.deleteAffiliation(conn, aid)
			print("Affiliation {} deleted from database".format(affName))

	return None

def import_csv(filename):
	""" imports contacts from CSV file
	"""

	# append file extension if not included
	if filename[-4:] != ".csv":
		filename += ".csv"

	try:
		with open(filename, "r") as csv_file:
			for line in csv_file:
				line = line[:-1]
				line = line.split(',')
				create_entry(first, last, mobile, affiliation)

	except Exception as e:
		print("Error processing CSV file: {}".format(e))
		return None
	else:
		print("Successfully imported from CSV")
		return None

def export_csv(filename):
	""" exports contacts to CSV file
	"""

	# append file extension if not included
	if filename[-4:] != ".csv":
		filename += ".csv"

	try:
		with open(filename, "w", newline='') as csv_file:
			people = db.getAllPeople(conn)
			people_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for person in people:
				people_writer.writerow([person[0], person[1], person[2], person[3]])

	except Exception as e:
		print("Error processing CSV file: {}".format(e))
		return None
	else:
		print("Successfully exported to CSV")
		return None

def import_vcf(filename):
	""" imports contacts from VCF file
	"""

	# append file extension if not included
	if filename[-4:] != ".vcf":
		filename += ".vcf"

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
				try:
					affiliation = entry.org.value[0]
				except:
					affiliation = None
				create_entry(first, last, mobile, affiliation)	

	except Exception as e:
		print("Error processing VCF file: {}".format(e))
		return None
	else:
		print("Successfully imported from VCF")
		return None

def export_vcf(filename):
	""" exports contacts to VCF file
	"""

	# append file extension if not included
	if filename[-4:] != ".vcf":
		filename += ".vcf"

	try:
		with open(filename, "a", newline='') as vcf_file:
			people = db.getAllPeople(conn)
			for person in people:
				new_person = vobject.vCard()
				new_person.add('n')
				new_person.n.value = vobject.vcard.Name(family=person[1], given=person[0])
				new_person.add('fn')
				new_person.fn.value = person[0] + " " + person[1]
				new_person.add('tel')
				new_person.tel.value = person[2]
				new_person.add('org')
				new_person.org.value = [person[3]]
				vcf_file.write(new_person.serialize())

	except Exception as e:
		print("Error processing VCF file: {}".format(e))
		return None
	else:
		print("Successfully exported to VCF")
		return None

def main():
	while True:
		print("\n-------------\n     ACE     \n-------------")
		print("(1) Show entire library")
		print("(2) Find affiliation")
		print("(3) Write a new entry")
		print("(4) Delete an entry")
		print("(5) Import from CSV")
		print("(6) Import from VCF")
		print("(7) Export to CSV")
		print("(8) Export to VCF")
		print("(0) Exit Program\n")
		
		# ensure choice is type int
		try:
			choice = int(input("Make a selection: "))
		except ValueError:
			print("\nPlease input a number.")
		except KeyboardInterrupt:
			break
		else:

			# CLI Formatting
			print()

			# print whole library
			if choice == 1:
				print_entire_library()

			# sort by available affiliations
			elif choice == 2:
				search_by_affilation()

			# write new entry
			elif choice == 3:
				try:
					first = input("Please enter first name: ")
					last = input("Please enter last name: ")
					mobile = input("Please enter mobile number: ")
					affiliation = input("Please enter affiliation: ")
				except KeyboardInterrupt:
					print("\nEntry Creation Aborted")
				else:
					create_entry(first, last, mobile, affiliation)

			# delete entry
			elif choice == 4:
				try:
					person = input('Please enter the name of the person you wish to delete (type "all" for all): ')
				except KeyboardInterrupt:
					print("\nEntry Deletion Aborted")
				else:
					delete_entry(person)

			# import from csv
			elif choice == 5:
				print("NOTE: CSV must be in format <first_name>,<last_name>,<mobile>,<affiliation>")
				try:
					filename = input("Please input CSV file name to import from (must be in current directory): ")
				except KeyboardInterrupt:
					print("\nCSV Import Aborted")
				else:
					import_csv(filename)

			# import from vcf
			elif choice == 6:
				try:
					filename = input("Please input VCF file name to import from (must be in current directory): ")
				except KeyboardInterrupt:
					print("\nVCF Import Aborted")
				else:
					import_vcf(filename)

			# export to csv
			elif choice == 7:
				print("NOTE: CSV will be in format <first_name>,<last_name>,<mobile>,<affiliation>")
				try:
					filename = input("Please input CSV file name to export to (will be in current directory): ")
				except KeyboardInterrupt:
					print("\nCSV Export Aborted")
				else:
					export_csv(filename)

			# export to vcf
			elif choice == 8:
				try:
					filename = input("Please input VCF file name to export to (will be in current directory): ")
				except KeyboardInterrupt:
					print("\nVCF Export Aborted")
				else:
					export_vcf(filename)

			# exit
			elif choice == 0:
				break

			# invalid choice
			else:
				print('\nInvalid choice. Please try again.')

	print("Goodbye!")
	conn.close()
	sys.exit()

if __name__ == "__main__":

	# argument parsing
	parser = argparse.ArgumentParser(description='A simple application designed to display and manipulate contact data')
	parser.add_argument("--config", default="config.yaml", type=str, help='Configuration YAML file to use')
	parser.add_argument("--test", default=False, action='store_true', help='Flag to use MySQL test credentials')
	args = parser.parse_args()
	config_file = args.config
	test = args.test

	# load configuration data
	try:
		with open(config_file, 'r') as file:
			config = yaml.load(file)
	except Exception as e:
		print("Error loading configuration data: ", e)
		sys.exit()

	# connect to database
	try:
		if test:
			conn = mysql.connector.connect(user=config['mysql_test']['user'],
										   password=config['mysql_test']['password'],
										   host=config['mysql_test']['host'],
										   database=config['mysql_test']['database'])
		else:
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
		sys.exit()

	# license boilerplate
	print("Archived Contact Engine Copyright (C) 2020 Nathan Weinberg\nThis program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.\nThis is free software, and you are welcome to redistribute it\nunder certain conditions; type `show c' for details.")
	main()
