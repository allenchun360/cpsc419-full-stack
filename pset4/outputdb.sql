CREATE TABLE departments(
    deptcode TEXT,
    deptname TEXT,
    PRIMARY KEY (deptcode)
);
CREATE INDEX department_code_index ON departments (deptcode);
CREATE TABLE courses(
    courseid INTEGER,
    subjectcode TEXT,
    coursenum TEXT,
    deptcode TEXT,
    title TEXT,
    descrip TEXT,
    prereqs TEXT,
    PRIMARY KEY (courseid),
    FOREIGN KEY (deptcode) REFERENCES departments (deptcode)
);
CREATE INDEX courses_id_index ON courses (courseid);
CREATE TABLE sections(
    courseid INTEGER,
    sectionid INTEGER,
    crn INTEGER,
    sectionnumber INTEGER,
    PRIMARY KEY (crn),
    FOREIGN KEY (courseid) REFERENCES courses (courseid)
);
CREATE INDEX sections_crn_index ON sections (crn);
CREATE TABLE meetings(
    meetingid INTEGER,
    crn INTEGER,
    timestring TEXT,
    locstring TEXT,
    PRIMARY KEY (meetingid)
    FOREIGN KEY (crn) REFERENCES sections (crn)
);
CREATE INDEX meetings_crn_index ON meetings (crn);
CREATE TABLE crosslistings(
    primarycourseid INTEGER,
    secondarycourseid INTEGER,
    FOREIGN KEY (primarycourseid) REFERENCES courses (courseid)
    FOREIGN KEY (secondarycourseid) REFERENCES courses (courseid)
);
CREATE INDEX crosslistings_courseid_index ON crosslistings (primarycourseid);
CREATE TABLE profs(
    profid INTEGER,
    profname TEXT,
    PRIMARY KEY (profid)
);
CREATE INDEX profs_profid_index ON profs (profid);
CREATE TABLE coursesprofs(
    courseid INTEGER,
    profid INTEGER,
    FOREIGN KEY (courseid) REFERENCES courses (courseid),
    FOREIGN KEY (profid) REFERENCES profs (profid)
);
CREATE INDEX coursesprofs_courseid_index ON coursesprofs (courseid);
CREATE INDEX coursesprofs_profid_index ON coursesprofs (profid);