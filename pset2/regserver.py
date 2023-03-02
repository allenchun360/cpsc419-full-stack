"""Code for regserver"""

import argparse
import sqlite3
from contextlib import closing
from pickle import load, dump
from os import name
from sys import exit, stderr
from socket import SOL_SOCKET, SO_REUSEADDR
import socket
from table import Table

DATABASE_URL = 'file:reg.sqlite?mode=ro'

def get_filter_terms():
    """User interface. Gets port from user and returns it"""
    parser = argparse.ArgumentParser(description='Server for the registrar application',
                                        prog='regserver.py', allow_abbrev=False,
                                        usage='%(prog)s ' + '[-h] port')

    parser.add_argument('port', help='the port at which ' +
                            'the server should listen')

    return parser.parse_args()

def get_filtered_courses(args, screen_width):
    """Takes in arguments and returns tables"""
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
                    add_str += "UPPER(departments.deptname) LIKE :dept "
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
                data = []
                while row is not None:
                    data.append(row)
                    row = cursor.fetchone()

                column_names = ["crns", "deptname", "subject", "num", "title"]
                test_table = Table(column_names=column_names, data=data, max_width = screen_width)

                return test_table

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

                tables = []

                stmt_str = "SELECT departments.deptcode, departments.deptname, "
                stmt_str += "CAST(courses.subjectcode AS text), "
                stmt_str += "CAST(courses.coursenum AS text) "
                stmt_str += "FROM (courses NATURAL JOIN departments) NATURAL JOIN sections WHERE "
                stmt_str += "CAST(sections.crn AS text) = ?"
                cursor.execute(stmt_str, [crn])

                raw_data = list(cursor.fetchall())
                print(raw_data)
                data = []
                for entry in raw_data:
                    print(entry[0])
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
                cursor.execute(stmt_str, [crn])

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
                cursor.execute(stmt_str, [crn])

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
                cursor.execute(stmt_str, [crn])

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
                cursor.execute(stmt_str, [crn])

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
                cursor.execute(stmt_str, [crn])

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
                cursor.execute(stmt_str, [crn])

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

def handle_client(sock):
    """implement functionality"""
    in_flo = sock.makefile(mode='rb')
    args = load(in_flo)
    screen_width = load(in_flo)
    action = load(in_flo)
    if args == '':
        print('The client crashed')
        return

    if action == "courses":
        courses = get_filtered_courses(args, screen_width)
    elif action == "details":
        courses = get_message(args)

    out_flo = sock.makefile(mode='wb')
    dump(courses, out_flo)
    out_flo.flush()

def main():
    """main"""
    try:
        port = int(get_filter_terms().port)

        server_sock = socket.socket()
        print('Opened server socket')
        if name != 'nt':
            server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            server_sock.bind(('', port))
        except socket.error:
            print('Unavailable port', file=stderr)
            exit(1)
        print('Bound server socket to port')
        server_sock.listen()
        print('Listening')

        while True:
            try:
                sock, client_addr = server_sock.accept()
                with sock:
                    print('Accepted connection')
                    print('Opened socket')
                    print('Server IP addr and port:',
                        sock.getsockname())
                    print('Client IP addr and port:', client_addr)
                    handle_client(sock)
            except socket.error as ex:
                print(ex, file=stderr)

    except socket.error as ex:
        print(ex, file=stderr)
        exit(1)

if __name__ == '__main__':
    main()
