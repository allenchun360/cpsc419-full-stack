"""accessing database"""

import sqlite3
from sys import exit
from contextlib import closing
from course import Course

DATABASE_URL = 'file:outputdb?mode=ro'

def get_filtered_courses(args):
    """Takes in arguments and returns tables"""

    if (args['d'] is None and args['s'] is None and args['n'] is None and
            args['t'] is None):
        return []

    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None,
                             uri=True) as connection:
            with closing(connection.cursor()) as cursor:

                stmt_str = "SELECT alias.crn, departments.deptname, courses.subjectcode, "
                stmt_str += "CAST(courses.coursenum AS text), courses.title "
                stmt_str += "FROM (courses NATURAL JOIN departments) NATURAL JOIN "
                stmt_str += "(SELECT courseid, CAST(crn AS text) AS crn "
                stmt_str += "FROM sections) AS alias WHERE "

                arg_dict = {}
                query_count = 0
                add_str = ""
                if args['d'] is not None:
                    query_count += 1
                    add_str += "UPPER(departments.deptname) LIKE :dept OR UPPER(departments.deptcode) LIKE :dept "
                    arg_dict["dept"] = "%" + args['d'].upper() + "%"
                if args['s'] is not None:
                    if query_count > 0:
                        add_str += "AND "
                    add_str += "UPPER(courses.subjectcode) LIKE :subj "
                    arg_dict["subj"] = "%" + args['s'].upper() + "%"
                    query_count += 1
                if args['n'] is not None:
                    if query_count > 0:
                        add_str += "AND "
                    add_str += "CAST(courses.coursenum AS text) LIKE :coursenum "
                    arg_dict["coursenum"] = "%" + args['n'] + "%"
                    query_count += 1
                if args['t'] is not None:
                    if query_count > 0:
                        add_str += "AND "
                    add_str += "UPPER(courses.title) LIKE :title "
                    arg_dict["title"] = "%" + args['t'] + "%"

                if len(arg_dict) != 0:
                    stmt_str += add_str
                else:
                    stmt_str += "TRUE "

                stmt_str += ("ORDER BY departments.deptname ASC, " +
                             "courses.coursenum ASC, alias.crn ASC")

                cursor.execute(stmt_str, arg_dict)

                row = cursor.fetchone()
                table = []

                while row is not None:
                    course = Course(crn=str(row[0]), deptname=str(row[1]),
                                    subjectcode=str(row[2]), coursenum=str(row[3]),
                                    title=str(row[4]))
                    table.append(course)
                    row = cursor.fetchone()

                return table

    except sqlite3.OperationalError:
        print("table not found")
        exit(1)
    except sqlite3.DatabaseError:
        print("database error: could not be found or corrupted")
        exit(1)

def get_message(crn):
    """Takes in arguments and returns tables"""
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None,
                             uri=True) as connection:
            with closing(connection.cursor()) as cursor:
                connection.row_factory = sqlite3.Row

                stmt_str = "SELECT departments.deptcode, departments.deptname, "
                stmt_str += "CAST(courses.subjectcode AS text), "
                stmt_str += "CAST(courses.coursenum AS text) "
                stmt_str += "FROM (courses NATURAL JOIN departments) NATURAL JOIN sections WHERE "
                stmt_str += "CAST(sections.crn AS text) = ?"
                cursor.execute(stmt_str, [crn])

                raw_data = list(cursor.fetchall())
                deptcode = []
                deptname = []
                subjectcode = []
                coursenum = []

                for entry in raw_data:
                    deptcode.append(entry[0])
                    deptname.append(entry[1])
                    subjectcode.append(entry[2])
                    coursenum.append(entry[3])

                if len(deptcode) == 0:
                    print("No course found")
                    return None

                stmt_str = "SELECT courses.title "
                stmt_str += "FROM courses NATURAL JOIN sections "
                stmt_str += "WHERE CAST(sections.crn AS text) = ?"
                cursor.execute(stmt_str, [crn])

                raw_data = list(cursor.fetchall())
                title = []
                for entry in raw_data:
                    title.append(entry[0])

                stmt_str = "SELECT courses.descrip "
                stmt_str += "FROM courses NATURAL JOIN sections "
                stmt_str += "WHERE CAST(sections.crn AS text) = ?"
                cursor.execute(stmt_str, [crn])

                raw_data = list(cursor.fetchall())
                descrip = []
                for entry in raw_data:
                    descrip.append(entry[0])

                stmt_str = "SELECT courses.prereqs "
                stmt_str += "FROM courses NATURAL JOIN sections "
                stmt_str += "WHERE CAST(sections.crn AS text) = ?"
                cursor.execute(stmt_str, [crn])

                raw_data = list(cursor.fetchall())
                prereqs = []
                for entry in raw_data:
                    prereqs.append(entry[0])

                stmt_str = "SELECT sections.sectionnumber, "
                stmt_str += "CAST(sections.crn AS text) AS crn, alias.timeloc "
                stmt_str += "FROM sections NATURAL JOIN (SELECT crn, "
                stmt_str += "group_concat((meetings.timestring || ' @ ' "
                stmt_str += "|| meetings.locstring), '|') "
                stmt_str += "AS timeloc FROM meetings GROUP BY crn) AS alias "
                stmt_str += "WHERE sections.courseid IN "
                stmt_str += "(SELECT courses.courseid FROM courses "
                stmt_str += "NATURAL JOIN sections WHERE "
                stmt_str += "CAST(sections.crn AS text) = ?) "
                stmt_str += "ORDER BY sections.sectionnumber ASC, crn ASC"
                cursor.execute(stmt_str, [crn])

                raw_data = list(cursor.fetchall())
                sectionnumber = []
                crn_list = []
                meetinginfo = []
                for entry in raw_data:
                    sectionnumber.append(entry[0])
                    crn_list.append(entry[1])
                    meetinginfo.append(entry[2])

                stmt_str = "SELECT courses.subjectcode, courses.coursenum "
                stmt_str += "FROM courses INNER JOIN crosslistings ON "
                stmt_str += "courses.courseid = crosslistings.secondarycourseid "
                stmt_str += "WHERE crosslistings.primarycourseid IN "
                stmt_str += "(SELECT courses.courseid FROM courses NATURAL JOIN "
                stmt_str += "sections WHERE CAST(sections.crn AS text) = ?) "
                stmt_str += "ORDER BY courses.subjectcode ASC, courses.coursenum ASC"
                cursor.execute(stmt_str, [crn])

                raw_data = list(cursor.fetchall())
                subjectcode_list = []
                coursenum_list = []
                for entry in raw_data:
                    subjectcode_list.append(entry[0])
                    coursenum_list.append(entry[1])

                stmt_str = "SELECT profs.profname "
                stmt_str += "FROM ((courses NATURAL JOIN sections) "
                stmt_str += "NATURAL JOIN coursesprofs) "
                stmt_str += "NATURAL JOIN profs WHERE CAST(sections.crn AS text) = ? "
                stmt_str += "ORDER BY profs.profname ASC"
                cursor.execute(stmt_str, [crn])

                raw_data = list(cursor.fetchall())
                professors = []
                for entry in raw_data:
                    professors.append(entry[0])

                course = Course(crn=crn_list, deptname=deptname, subjectcode=subjectcode,
                                coursenum=coursenum, title=title, subjectcode_list=subjectcode_list,
                                coursenum_list=coursenum_list, deptcode=deptcode, descrip=descrip,
                                prof=professors, prereqs=prereqs, sectionnumber=sectionnumber,
                                meetinginfo=meetinginfo)

                return course

    except sqlite3.OperationalError:
        print("table not found")
        exit(1)
    except sqlite3.DatabaseError:
        print("database error: could not be found or corrupted")
        exit(1)
