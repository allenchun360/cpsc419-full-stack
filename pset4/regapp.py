"""regapp"""
from datetime import datetime
from flask import Flask, request, make_response
from flask import render_template
from database import get_filtered_courses, get_message

#-----------------------------------------------------------------------

APP = Flask(__name__, template_folder='.')

#-----------------------------------------------------------------------

def get_current_date():
    """get current date"""
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d %H:%M %p")
    return date_time

#-----------------------------------------------------------------------
@APP.route('/', methods=['GET'])
def home_form():
    """home form"""
    prev_deptname = request.cookies.get('prev_department')
    prev_subjectcode = request.cookies.get('prev_subject')
    prev_coursenum = request.cookies.get('prev_coursenum')
    prev_title = request.cookies.get('prev_title')

    if (prev_deptname is None and prev_subjectcode is None and
            prev_coursenum is None and prev_title is None):
        table = []
        prev_deptname = ''
        prev_subjectcode = ''
        prev_coursenum = ''
        prev_title = ''
    else:
        if prev_deptname is None:
            prev_deptname = ''
        if prev_subjectcode is None:
            prev_subjectcode = ''
        if prev_coursenum is None:
            prev_coursenum = ''
        if prev_title is None:
            prev_title = ''
        args = {'d': prev_deptname, 's': prev_subjectcode, 'n': prev_coursenum, 't': prev_title}
        table = get_filtered_courses(args)

    html = render_template('searchform.html',
                           current_date=get_current_date(),
                           table=table,
                           prev_department=prev_deptname,
                           prev_subject=prev_subjectcode,
                           prev_coursenum=prev_coursenum,
                           prev_title=prev_title)
    response = make_response(html)

    return response

#-----------------------------------------------------------------------

@APP.route('/search', methods=['GET'])
def search_form():
    """search form"""
    deptname = request.args.get('Department')
    if deptname is None:
        deptname = ''
    subjectcode = request.args.get('Subject')
    if subjectcode is None:
        subjectcode = ''
    coursenum = request.args.get('Course Number')
    if coursenum is None:
        coursenum = ''
    title = request.args.get('Title')
    if title is None:
        title = ''

    args = {'d': deptname, 's': subjectcode, 'n': coursenum, 't': title}
    table = get_filtered_courses(args)

    html = render_template('searchform.html',
                           current_date=get_current_date(),
                           table=table,
                           prev_department=deptname,
                           prev_subject=subjectcode,
                           prev_coursenum=coursenum,
                           prev_title=title)

    response = make_response(html)
    response.set_cookie('prev_department', deptname)
    response.set_cookie('prev_subject', subjectcode)
    response.set_cookie('prev_coursenum', coursenum)
    response.set_cookie('prev_title', title)
    return response

#-----------------------------------------------------------------------

@APP.route('/details', methods=['GET'])
def search_results():
    """search results"""

    prev_department = request.cookies.get('prev_department')
    if prev_department is None:
        prev_department = ''
    prev_subject = request.cookies.get('prev_subject')
    if prev_subject is None:
        prev_subject = ''
    prev_coursenum = request.cookies.get('prev_coursenum')
    if prev_coursenum is None:
        prev_coursenum = ''
    prev_title = request.cookies.get('prev_title')
    if prev_title is None:
        prev_title = ''

    crn = request.args.get('crn')
    # print(crn)
    if crn is None:
        error_msg = 'Please enter a crn.'
        html = render_template('error.html',
                               error_msg=error_msg)
        response = make_response(html)
        return response

    course = get_message(crn)

    if course is None:
        error_msg = 'Please enter a valid crn.'
        html = render_template('error.html',
                               error_msg=error_msg)
        response = make_response(html)
        return response

    html = render_template('searchresults.html',
                           current_date=get_current_date(),
                           course=course)
    response = make_response(html)
    response.set_cookie('prev_department', prev_department)
    response.set_cookie('prev_subject', prev_subject)
    response.set_cookie('prev_coursenum', prev_coursenum)
    response.set_cookie('prev_title', prev_title)

    return response
