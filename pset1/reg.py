"""Code for reg"""

import argparse
from sys import exit
import sqlite3
from contextlib import closing
from table import Table

DATABASE_URL = 'file:reg.sqlite?mode=ro'

def get_filter_terms():
    """User interface. Gets arguments from user and returns them"""
    parser = argparse.ArgumentParser(prog='reg.py', allow_abbrev=False, usage='%(prog)s ' +
                                    '[-h] [-d deptcode] [-s subjectcode] [-n num] [-t title]')

    parser.add_argument('-d', metavar = "deptcode", help='show only those ' +
                            'classes whose department code contains dept')
    parser.add_argument('-s', metavar = "subjectcode", help='show only those ' +
                            'classes whose subjectcode contains subject')
    parser.add_argument('-n', metavar = "num", help='show only those ' +
                            'classes whose course number contains num')
    parser.add_argument('-t', metavar = "title", help='show only those ' +
                            'classes whose course title contains title')

    return parser.parse_args()

def get_filtered_courses(args):
    """Takes in arguments and returns tables"""
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None,
            uri=True) as connection:
            with closing(connection.cursor()) as cursor:

                connection.row_factory = sqlite3.Row
                stmt_str = "SELECT departments.deptname, courses.subjectcode, "
                stmt_str += "CAST(courses.coursenum AS text), courses.title, alias.crn "
                stmt_str += "FROM (courses NATURAL JOIN departments) NATURAL JOIN "
                stmt_str += "(SELECT courseid, group_concat(CAST(crn AS text), '|') AS crn "
                stmt_str += "FROM sections GROUP BY courseid) AS alias WHERE "

                arg_dict = {}
                query_count = 0
                add_str = ""
                if args.d is not None:
                    query_count += 1
                    add_str += "UPPER(departments.deptcode) LIKE :dept "
                    arg_dict["dept"] = "%" + args.d.upper() + "%"
                if args.s is not None:
                    if query_count > 0:
                        add_str += "AND "
                    add_str += "UPPER(courses.subjectcode) LIKE :subj "
                    arg_dict["subj"] = "%" + args.s.upper() + "%"
                    query_count += 1
                if args.n is not None:
                    if query_count > 0:
                        add_str += "AND "
                    add_str += "CAST(courses.coursenum AS text) LIKE :coursenum "
                    arg_dict["coursenum"] = "%" + args.n + "%"
                    query_count += 1
                if args.t is not None:
                    if query_count > 0:
                        add_str += "AND "
                    add_str += "UPPER(courses.title) LIKE :title "
                    arg_dict["title"] = "%" + args.t + "%"

                if len(arg_dict) != 0:
                    stmt_str += add_str
                else:
                    stmt_str += "TRUE "

                stmt_str += ("ORDER BY departments.deptname ASC, courses.subjectcode ASC, " +
                                        "courses.coursenum ASC, courses.title ASC, alias.crn ASC")

                cursor.execute(stmt_str, arg_dict)

                raw_data = list(cursor.fetchall())
                data = []
                for entry in raw_data:
                    data.append(list(entry))

                if len(data) == 0:
                    print("No results.")
                    exit(0)

                column_names = ["deptname", "subject", "num", "title", "crns"]
                test_table = Table(column_names=column_names, data=data, format_str="wwwwp")

                return test_table

    except sqlite3.OperationalError:
        print("table not found")
        exit(1)
    except sqlite3.DatabaseError:
        print("database error: could not be found or corrupted")
        exit(1)

def output_courses(test_table):
    """"Prints table"""
    print(test_table)

def main():
    """Main"""
    filters = get_filter_terms()
    courses = get_filtered_courses(filters)
    output_courses(courses)

main()
