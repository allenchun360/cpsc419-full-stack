"""Code for regdetails"""

import argparse
from sys import exit
from contextlib import closing
import sqlite3
from table import Table

DATABASE_URL = 'file:reg.sqlite?mode=ro'

def get_filter_terms():
    """User interface. Gets arguments from user and returns them"""
    parser = argparse.ArgumentParser(prog='regdetails.py', allow_abbrev=False,
                                        usage='%(prog)s [-h] crn')

    parser.add_argument('crn', help='the id of the course whose details should be shown')
    args = parser.parse_args()

    return args

def get_filtered_courses(args):
    """Takes in arguments and returns tables"""
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None,
            uri=True) as connection:
            with closing(connection.cursor()) as cursor:
                connection.row_factory = sqlite3.Row

                tables = []

                stmt_str = "SELECT departments.deptcode, departments.deptname, "
                stmt_str += "CAST(courses.subjectcode AS text), "
                stmt_str += "CAST(courses.coursenum AS text) "
                stmt_str += "FROM (courses NATURAL JOIN departments) NATURAL JOIN sections WHERE "
                stmt_str += "CAST(sections.crn AS text) = ?"
                cursor.execute(stmt_str, [args.crn])

                raw_data = list(cursor.fetchall())
                data = []
                for entry in raw_data:
                    data.append(list(entry))

                if len(data) == 0:
                    print("No course found")
                    exit(0)

                column_names = ["deptcode", "deptname", "subjectcode", "coursenum"]
                test_table1 = Table(column_names=column_names, data=data)
                tables.append(test_table1)

                stmt_str = "SELECT courses.title "
                stmt_str += "FROM courses NATURAL JOIN sections "
                stmt_str += "WHERE CAST(sections.crn AS text) = ?"
                cursor.execute(stmt_str, [args.crn])

                raw_data = list(cursor.fetchall())
                data = []
                for entry in raw_data:
                    data.append(list(entry))

                column_names = ["title"]
                test_table2 = Table(column_names=column_names, data=data)
                tables.append(test_table2)

                stmt_str = "SELECT courses.descrip "
                stmt_str += "FROM courses NATURAL JOIN sections "
                stmt_str += "WHERE CAST(sections.crn AS text) = ?"
                cursor.execute(stmt_str, [args.crn])

                raw_data = list(cursor.fetchall())
                data = []
                for entry in raw_data:
                    data.append(list(entry))

                column_names = ["descrip"]
                test_table3 = Table(column_names=column_names, data=data)
                tables.append(test_table3)

                stmt_str = "SELECT courses.prereqs "
                stmt_str += "FROM courses NATURAL JOIN sections "
                stmt_str += "WHERE CAST(sections.crn AS text) = ?"
                cursor.execute(stmt_str, [args.crn])

                raw_data = list(cursor.fetchall())
                data = []
                for entry in raw_data:
                    data.append(list(entry))

                column_names = ["prereqs"]
                test_table4 = Table(column_names=column_names, data=data)
                tables.append(test_table4)

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
                cursor.execute(stmt_str, [args.crn])

                raw_data = list(cursor.fetchall())
                data = []
                for entry in raw_data:
                    data.append(list(entry))

                column_names = ["sectionnumber", "crn", "meetinginfo"]
                test_table5 = Table(column_names=column_names, data=data, format_str = "wpp")
                tables.append(test_table5)

                stmt_str = "SELECT courses.subjectcode, courses.coursenum "
                stmt_str += "FROM courses INNER JOIN crosslistings ON "
                stmt_str += "courses.courseid = crosslistings.secondarycourseid "
                stmt_str += "WHERE crosslistings.primarycourseid IN "
                stmt_str += "(SELECT courses.courseid FROM courses NATURAL JOIN "
                stmt_str += "sections WHERE CAST(sections.crn AS text) = ?) "
                stmt_str += "ORDER BY courses.subjectcode ASC, courses.coursenum ASC"
                cursor.execute(stmt_str, [args.crn])

                raw_data = list(cursor.fetchall())
                data = []
                for entry in raw_data:
                    data.append(list(entry))

                column_names = ["subjectcode", "coursenum"]
                test_table6 = Table(column_names=column_names, data=data)
                tables.append(test_table6)

                stmt_str = "SELECT profs.profname "
                stmt_str += "FROM ((courses NATURAL JOIN sections) "
                stmt_str += "NATURAL JOIN coursesprofs) "
                stmt_str += "NATURAL JOIN profs WHERE CAST(sections.crn AS text) = ? "
                stmt_str += "ORDER BY profs.profname ASC"
                cursor.execute(stmt_str, [args.crn])

                raw_data = list(cursor.fetchall())
                data = []
                for entry in raw_data:
                    data.append(list(entry))

                column_names = ["professors"]
                test_table7 = Table(column_names=column_names, data=data)
                tables.append(test_table7)

                return tables

    except sqlite3.OperationalError:
        print("table not found")
        exit(1)
    except sqlite3.DatabaseError:
        print("database error: could not be found or corrupted")
        exit(1)

def output_courses(test_tables):
    """"Prints table"""
    count = 0
    for table in test_tables:
        if count != 0:
            print()
        print(table)
        count += 1

def main():
    """Main"""
    filters = get_filter_terms()
    courses = get_filtered_courses(filters)
    output_courses(courses)

main()
