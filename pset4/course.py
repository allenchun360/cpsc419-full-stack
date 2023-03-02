"""course class"""

class Course:
    """course class"""

    def __init__(self, crn=None, deptname=None, subjectcode=None, coursenum=None, title=None,
                 subjectcode_list=None, coursenum_list=None, deptcode=None, descrip=None,
                 prof=None, prereqs=None, sectionnumber=None, meetinginfo=None):
        self._crn = crn
        self._deptname = deptname
        self._subjectcode = subjectcode
        self._coursenum = coursenum
        self._title = title

        self._subjectcode_list = subjectcode_list
        self._coursenum_list = coursenum_list
        self._deptcode = deptcode
        self._descrip = descrip
        self._prof = prof
        self._prereqs = prereqs
        self._sectionnumber = sectionnumber
        self._meetinginfo = meetinginfo

    def get_crn(self):
        """get crn"""
        return self._crn

    def get_deptname(self):
        """get deptname"""
        return self._deptname

    def get_subjectcode(self):
        """get subjectcode"""
        return self._subjectcode

    def get_coursenum(self):
        """get coursenum"""
        return self._coursenum

    def get_title(self):
        """get title"""
        return self._title

    def get_subjectcode_list(self):
        """get subjectcode list"""
        return self._subjectcode_list

    def get_coursenum_list(self):
        """get coursenum list"""
        return self._coursenum_list

    def get_deptcode(self):
        """get deptcode"""
        return self._deptcode

    def get_descrip(self):
        """get description"""
        return self._descrip

    def get_prof(self):
        """get professors"""
        return self._prof

    def get_prereqs(self):
        """get prereqs"""
        return self._prereqs

    def get_sectionnumber(self):
        """get section number"""
        return self._sectionnumber

    def get_meetinginfo(self):
        """get meeting info"""
        return self._meetinginfo
