'''
Created on May 5, 2016

@author: Zach
'''
import requests, datetime, os

default_root_url = "https://ntst.umd.edu/soc"
semesters = {"Spring": "01", "Summer": "05", "Fall": "08", "Winter": "12"}
years = range(2014, datetime.datetime.now().year + 1)
root_dir = "C:/WAMP/courses"

def get_semester(month):
    """Returns semester of given month number."""
    for semester in sorted(semesters):
        if month >= int(semesters[semester]):
            return semester
        
current_year = datetime.datetime.now().year
current_semester = get_semester(datetime.datetime.now().month)

def parse_between(text, start, end):
    """Returns all substrings occurring between given start and end strings in the given text."""
    if start in text and end in text:
        data = []
        string = text.split(start)
        # we know no data will be in first position
        del string[0]
        for substring in string:
            data.append(substring.partition(end)[0])
        return data
    else:
        return ["None"]
    
def parse_course_text(text):
    """Returns prerequisites, restrictions, and credit equivalences from given string."""  
         
    prerequisites, restrictions, equivalences, description = "", "", "", ""
    
    for string in text:
        if "Credit only granted for: " in string or "Restriction:" in string or "Prerequisite: " in string:
            
            if "Also offered as: " in string:
                before = string.partition("Also offered as: ")
                after = before[2].partition(".")
                string = before[0] + after[2]
                equivalences = after[0]
            
            # add "Formerly" to description
            string = string.partition("Formerly: ")
            description += string[1] + string[2]
            
            # parse equivalences
            string = string[0].partition("Credit only granted for: ")
            if string[2] is not "":
                equivalences = ";".join((equivalences, string[2].replace(",", ";").replace(" or ", ";").replace(" and ", ";").replace(".", "")))
            
            # add "Additional information" to description
            equivalences = equivalences.partition("Additional information: ")
            description += equivalences[1] + equivalences[2]
            
            # format equivalences into string with semicolon delimiter
            equivalences = equivalences[0]
            
            # parse restrictions
            string = string[0].partition("Restriction: ")
            restrictions = string[2]
            
            # add "also offered" to equivalences
            restrictions = restrictions.partition("Also offered as: ")
            equivalences = ";".join((equivalences, restrictions[2]))
            restrictions = restrictions[0]
            
            # parse prerequisites
            string = string[0].partition("Prerequisite: ")
            prerequisites = string[2]
            
        # else assume it is a description
        else:
            description = " ".join((string, description))
    
    prerequisites = prerequisites.strip(";").replace(" ", "").replace(";;", ";")
    if prerequisites is "":
        prerequisites = "None"
        
    restrictions = restrictions.strip(";").replace(" ", "").replace(";;", ";")
    if restrictions is "":
        restrictions = "None"
    
    equivalences = equivalences.strip(";").replace(" ", "").replace(";;", ";")
    if equivalences is "":
        equivalences = "None"
        
    description = description.strip(";")
    if description is "":
        description = "None"
    
    return (prerequisites, restrictions, equivalences, description)

def parse_courses_to_file(output_file, semester=current_semester, year=current_year, root_url=default_root_url):
    """Write course data to file"""
    output_file = open(output_file, "w")
    print("Writing course data to " + output_file.name)
    print(parse_courses(semester, year, root_url), file=output_file)
    output_file.close()

def get_majors(root_url=default_root_url):
    """Returns list of majors parsed from main page."""
    return parse_between(requests.get(root_url).text, '<span class="prefix-abbrev push_one two columns">', '</span>')

def parse_courses(semester=current_semester, year=current_year, root_url=default_root_url):
    """Returns course data in CSV format for given semester and year"""
    print("Downloading course data for " + semester + " " + str(year) + " semester...")
    
    majors = get_majors(root_url)
    
    semester_csv = ",".join(("Course ID", "Title", "Major", "Credits", "Grading Methods", "GenEd", "Prerequisites", "Restrictions", "Equivalences", "Description")) + "\n"
    
    for major in majors:
        major_url = root_url + "/" + str(year) + semesters[semester] + "/" + major
        # get part of HTML relevant to course info and split into courses
        major_html = requests.get(major_url).text.partition('<div class="courses-container">')[2].partition('<script type="text/javascript">')[0].split('<div id="' + major)
        del major_html[0]
        
        for course_html in major_html:
            course_id = course_html.partition('" class="course">')[0]
            course_title = parse_between(course_html, '<span class="course-title">', '</span>')[0].replace('"', "'")
            course_min_credits = parse_between(course_html, '<span class="course-min-credits">', '</span>')[0]
            grading_methods = ";".join(parse_between(parse_between(course_html, '<span class="grading-method">', '</span>')[0], '<abbr title="', '"><span>')[0].split(", "))
            
            gen_ed_codes = []
            for gen_ed_code in parse_between(parse_between(course_html, '<div class="gen-ed-codes-group six columns">', '</div>')[0], '<span class="course-subcategory">', '</span>'):
                gen_ed_codes.append(parse_between(gen_ed_code, '">', '</a>')[0])
            gen_ed_codes = ";".join(gen_ed_codes)
            
            prerequisites, restrictions, equivalences, description = parse_course_text(parse_between(course_html, '<div class="approved-course-text">', '</div>'))
            
            # put into CSV sanitized format
            semester_csv += '"' + '","'.join((course_id, course_title, major, course_min_credits, grading_methods, gen_ed_codes, prerequisites, restrictions, equivalences, description)) + '"' + "\n"
        
    return semester_csv

class Course:
    """Course with major, course_id, course_title, credits, grading_methods methods, GenEd gen_ed_codes, prerequisites, and description."""
    def __init__(self, course_id, course_title, major, course_min_credits, grading_methods, gen_ed_codes, prerequisites, restrictions, equivalences, description):
        self.major = major
        self.course_id = course_id
        self.course_title = course_title
        self.min_credits = course_min_credits
        self.grading_methods = grading_methods
        self.gen_ed_codes = gen_ed_codes.split(";")
        self.prerequisites = prerequisites
        self.restrictions = restrictions
        self.equivalences = equivalences.split(";")
        self.description = description
        self.years = {}
    
    def __str__(self):
        return self.major + self.course_id + " " + self.course_title + "\n" + "Major: " + self.major + "\n" + "Credits: " + self.min_credits + "\n" + "Grading methods: " + str(self.grading_methods) + "\n" + "GenEd: " + str(self.gen_ed_codes) + "\n" + "Prerequisites: " + str(self.prerequisites) + "\n" + "Restrictions: " + str(self.restrictions) + "\n" + "Equivalences: " + str(self.equivalences) + "\n" + "Description: " + self.description

years = range(2014, datetime.datetime.now().year + 1)
root_dir = "C:/Users/Zach/Desktop/courses"
courses = {}

def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)

for year in years:
    for semester in sorted(semesters):
        semester_csv = root_dir + "/semesters/" + str(year) + "_" + str(semesters[semester]) + "_" + semester + ".csv"
        if not os.path.isfile(semester_csv):
            ensure_dir(semester_csv.rsplit("/", 1)[0])
            parse_courses_to_file(semester_csv, semester=semester, year=year)
        else:
            print("Data file " + semester_csv + " already exists.")
        
        data = open(semester_csv, "r").readlines()
        del data[0]
        del data[len(data) - 1]
                
        for line in data:
            values = line.strip("\n").strip('"').split('","')
            course_id, course_title, major, course_min_credits, grading_methods, course_subcategory, prerequisites, restrictions, equivalences, description = values
            course = Course(course_id, course_title, major, course_min_credits, grading_methods, course_subcategory, prerequisites, restrictions, equivalences, description)
            
            name = major + course_id
            
            if name not in courses:
                courses[name] = course
                
            if year not in courses[name].years:
                courses[name].years[year] = []

            courses[name].years[year].append(semester)

courses_html = open(root_dir + "/index.html", "w")
print("<!DOCTYPE=html>\n<html>", file=courses_html)
print("<title>Courses</title>\n<body>", file=courses_html)
print("<h1>Courses</h1>", file=courses_html)
print('<p>\n<a href="/">Back to home.</a>\n</p>', file=courses_html)
print('<p>\n<a href="semesters">Semester data.</a>\n</p>', file=courses_html)

print("<body>\n<p>", file=courses_html)

for course in sorted(courses):
    major = courses[course].major
    course_id = courses[course].course_id
    course_title = courses[course].course_title
    
    path = root_dir +  "/" + major + "/" + course_id
    ensure_dir(path)
    course_html = open(path + "/index.html", "w")
    header = course_id + ": " + course_title
    
    print('<a href="' + path + '">' + major + course_id + ': ' + course_title + '</a><br>', file=courses_html, end="\n")
    
    print("<!DOCTYPE=html>\n<html>", file=course_html)
    print("<title>" + header + "</title>", file=course_html)
    
    print("<h1>" + header + "</h1>", file=course_html)
        
    print('<p>\n<a href="/courses">' + "Back to courses</a>\n</p>", file=course_html)
    
    print("<body>\n<p>\n<pre>\n" + str(courses[course]) + "\n</p>", file=course_html)

    print("<p>", file=course_html)
    for year in sorted(courses[course].years):
        print(year, file=course_html)
        for semester in courses[course].years[year]:
            print(semester, file=course_html)
    print("</pre></p>", file=course_html, end="\n\n")
      
    print("<br>" + course_id + " OurUMD page<br>", file=course_html)
    print('<iframe src="http://www.ourumd.com/class/' + major + course_id + '" height="50%" width="100%"></iframe>', file=course_html)
    
    print("</body>\n</html>", file=course_html)
    
    course_html.close()
    
print("</p>\n</body>\n</html>", file=courses_html)
courses_html.close()