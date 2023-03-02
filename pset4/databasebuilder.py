import argparse
import json
import os
import requests
from sqlite3 import connect
from dotenv import load_dotenv, find_dotenv
from progressbar import progressbar
from codes import DEPARTMENTS
#-----------------------------------------------------------------------

# DATABASE_URL = 'file:' outputdb?mode=ro'

#-----------------------------------------------------------------------

load_dotenv(find_dotenv())
API_KEY = os.getenv('API_KEY')

#-----------------------------------------------------------------------

def get_courses(subject_code, term_code):
    """get courses"""
    url = "https://gw.its.yale.edu/soa-gateway/courses/webservice/v3/index"
    params = dict(apikey=API_KEY, subjectCode=subject_code, termCode=term_code)
    response = requests.get(url, params=params)
    return json.loads(response.content)

def get_all_subjects():
    """get all codes"""
    url = "https://gw.its.yale.edu/soa-gateway/course/webservice/v2/subjects"
    params = dict(apikey=API_KEY)
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return json.loads(response.content)
    return None

#-----------------------------------------------------------------------

def get_filter_terms():
    """User interface. Gets arguments from user and returns them"""
    parser = argparse.ArgumentParser(description="Application to download " +
									 "a list of all courses available in a " +
									 "particular term (or the current term) at " +
									 "Yale and store them in a SQLite database named outputdb.",
									 prog='databasebuilder.py', allow_abbrev=False, usage='%(prog)s ' +
                                    '[-h] [-t termcode] outputdb')

    parser.add_argument('-t', "--termcode", help='Four-digit year followed by two-digit term code.')
    parser.add_argument('outputdb', help='File in which to store the SQLite database created by this application.')
    # parser.add_argument('-n', metavar = "num", help='show only those ' +
    #                         'classes whose course number contains num')
    # parser.add_argument('-t', metavar = "title", help='show only those ' +
    #                         'classes whose course title contains title')

    return parser.parse_args()

def insert_dept(deptcode, deptname, db_file):
	con = connect(db_file)
	cur = con.cursor()
	query = "INSERT INTO departments (deptcode, deptname) VALUES (?, ?)"
	# query += "WHERE NOT EXISTS ("
	# query += "SELECT username FROM users WHERE username = {})".format(username)
	cur.execute(query, (deptcode, deptname))#, [(firstname, lastname, username, password), username])
	con.commit()
	con.close()

def insert_courses(subjectcode, coursenum, deptname, title, descrip, prereqs, db_file):
	con = connect(db_file)
	cur = con.cursor()
	cur.execute("SELECT deptcode from departments WHERE deptname = ?", [deptname])
	row = cur.fetchone()
	# print(f"deptname stuff: {row}")
	deptcode = row[0]

	query = "INSERT INTO courses (subjectcode, coursenum, deptcode, title, descrip, prereqs) VALUES (?, ?, ?, ?, ?, ?)"
	# query += "WHERE NOT EXISTS ("
	# query += "SELECT username FROM users WHERE username = {})".format(username)
	cur.execute(query, (subjectcode, coursenum, deptcode, title, descrip, prereqs))#, [(firstname, lastname, username, password), username])
	con.commit()
	con.close()

def insert_sections(subjectcode, coursenum, sectionnumber, crn, deptcode, title, descrip, prereqs, db_file):
	con = connect(db_file)
	cur = con.cursor()
	cur.execute("SELECT courseid from courses WHERE subjectcode = ? AND coursenum = ? AND deptcode = ? AND title = ? AND descrip = ? AND prereqs = ?", 
				(subjectcode, coursenum, deptcode, title, descrip, prereqs))
	row = cur.fetchone()
	if row is not None:
		courseid = row[0]
	

	# for entry in rows:
	# courseid = row[0]
	# 	# print(f"courseid stuff: {row}")
	# 	for course in courses:
	# 		if subjectnumber == course['subjectNumber']:
	# 			crn = course['crn']
		query = "INSERT INTO sections (courseid, sectionid, crn, sectionnumber) VALUES (?, ?, ?, ?)"
	# 			# query += "WHERE NOT EXISTS ("
	# 			# query += "SELECT username FROM users WHERE username = {})".format(username)
		cur.execute(query, (courseid, courseid, crn, sectionnumber))#, [(firstname, lastname, username, password), username])
	con.commit()
	con.close()

def insert_meetings(crn, timestring, locstring, db_file):
	con = connect(db_file)
	cur = con.cursor()
	query = "INSERT INTO meetings (crn, timestring, locstring) VALUES (?, ?, ?)"
	cur.execute(query, (crn, timestring, locstring))#, [(firstname, lastname, username, password), username])
	con.commit()
	con.close()

def insert_crosslistings(primarycourseid, secondarycourseid, db_file):
	con = connect(db_file)
	cur = con.cursor()
	query = "INSERT INTO crosslistings (primarycourseid, secondarycourseid) VALUES (?, ?)"
	# query += "WHERE NOT EXISTS ("
	# query += "SELECT username FROM users WHERE username = {})".format(username)
	cur.execute(query, (primarycourseid, secondarycourseid))#, [(firstname, lastname, username, password), username])
	con.commit()
	con.close()

def insert_profs(profname, db_file):
	con = connect(db_file)
	cur = con.cursor()
	query = "INSERT INTO profs (profname) VALUES (?)"
	# query += "WHERE NOT EXISTS ("
	# query += "SELECT username FROM users WHERE username = {})".format(username)
	cur.execute(query, (profname,))#, [(firstname, lastname, username, password), username])
	con.commit()
	con.close()

def insert_coursesprofs(courseid, profid, db_file):
	con = connect(db_file)
	cur = con.cursor()
	query = "INSERT INTO coursesprofs (courseid, profid) VALUES (?, ?)"
	cur.execute(query, (courseid, profid))#, [(firstname, lastname, username, password), username])
	con.commit()
	con.close()

def main():
	args = get_filter_terms()

	all_subjects = get_all_subjects()
	# print(all_courses)
	# course_list = []
	outputdb = args.outputdb
	termcode = args.termcode

	for key, value in DEPARTMENTS.items():
		insert_dept(deptcode=key, deptname=value, db_file=outputdb)

	course_count = 1
	prof_count = 1
	meeting_index = 0
	
	for i in progressbar(range(len(all_subjects))):
		courses = get_courses(all_subjects[i]['code'], termcode)
		for course in courses:
			if course['cSectionStatus'] == 'A':
				# insert_dept(deptcode=course['department'], deptname=DEPARTMENTS[course['department']], db_file=outputdb)
				insert_courses(subjectcode=course['subjectCode'], coursenum=course['courseNumber'],
							   deptname=DEPARTMENTS[course['department']], title=course['courseTitle'], descrip=course['description'],
							   prereqs=course['prerequisites'], db_file=outputdb)
							   
		for course in courses:
			if course['cSectionStatus'] == 'A':
				insert_sections(subjectcode=course['subjectCode'], coursenum=course['courseNumber'], sectionnumber=course['sectionNumber'], crn=course['crn'], deptcode=course['department'], title=course['courseTitle'], descrip=course['description'], prereqs=course['prerequisites'], db_file=outputdb)

				if (len(course['meetingPattern']) ==
					len(course['meetingPatternLocation'])):
					for i in range(len(course['meetingPattern'])):
						insert_meetings(crn=course['crn'], timestring=course['meetingPattern'][i], locstring=course['meetingPatternLocation'][i], db_file=outputdb)
						meeting_index += 1
				elif (len(course['meetingPattern']) >
					len(course['meetingPatternLocation'])):
					htba = False
					if (("HTBA" in course['meetingPattern'][0]) or
							("HTBA" in course['meetingPattern'][-1])):
						htba = True

					if htba is False: #2nd case
						if len(course['meetingPatternLocation']) != 0:
							location = course['meetingPatternLocation'][0]
							for i in course['meetingPattern']:
								insert_meetings(crn=course['crn'], timestring=i, locstring=location, db_file=outputdb)
								meeting_index += 1
						else:
							for i in course['meetingPattern']:
								# meetinginfo.append("")
								insert_meetings(crn=course['crn'], timestring="", locstring="", db_file=outputdb)
								meeting_index += 1
								
					else: #3rd case
						for (i, value) in enumerate(course['meetingPattern']):
							if i > (len(course['meetingPatternLocation']) - 1):
								insert_meetings(crn=course['crn'], timestring="", locstring="", db_file=outputdb)
							else:
								insert_meetings(crn=course['crn'], timestring=value, locstring=course['meetingPatternLocation'][i], db_file=outputdb)
							meeting_index += 1
					# if index < len(course['meetingPatternLocation']):
					# 	insert_meetings(meetingid=index, crn=course['crn'], timestring=course['meetingPattern'], locstring=course['meetingPatternLocation'], db_file=outputdb)
					# else:
					# 	insert_meetings(meetingid=index, crn=course['crn'], timestring=course['meetingPattern'], locstring=course['meetingPatternLocation'], db_file=outputdb)
				for sec_course in course['scndXLst']:
					insert_crosslistings(primarycourseid=course['primXLst'], secondarycourseid=sec_course, db_file=outputdb)
				
				for prof in course['instructorList']:
					insert_profs(profname=prof, db_file=outputdb)
					insert_coursesprofs(courseid=course_count, profid=prof_count, db_file=outputdb)
					prof_count += 1
				# insert_coursesprofs(courseid=course[''], profid, db_file)
				
				course_count += 1
			# course_list.append(j)
			# print(j)


	# out_file = open("cachecourses.json", "w", encoding="utf8")
	# json.dump(course_list, out_file)
	# out_file.close()

		# insert_courses(outputdb)
		# insert_coursesprofs(outputdb)
		# insert_crosslistings(outputdb)
		# insert_dept(outputdb)
		# insert_meetings(outputdb)
		# insert_profs(outputdb)
		# insert_sections(outputdb)


if __name__ == '__main__':
	main()