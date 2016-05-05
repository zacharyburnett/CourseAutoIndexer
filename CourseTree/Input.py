'''
Created on May 4, 2016

@author: Zach
'''
import requests, datetime, time

semesters = {"Spring": "01", "Summer": "05", "Fall": "08", "Winter": "12"}

root_url = "https://ntst.umd.edu/soc"
output_csv = "C:/Users/Zach/Desktop/courses.csv"

semester = "Spring"

year = datetime.datetime.now().year
month = datetime.datetime.now().month

def get_semester(month):
    """Returns semester of given month number."""
    for semester in semesters:
        if month >= int(semesters[semester]):
            return semester
        
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
        return [""]
    
def parse_course_info(text):
    """Returns prerequisites, restrictions, and credit equivalences from given string."""  
         
    string = text.partition("Formerly: ")[0].partition("Credit only granted for: ")
    equivalences = ";".join(string[2].replace("or", "").replace(",", "").split())
    
    string = string[0].partition("Restriction: ")
    restrictions = string[2]
    
    string = string[0].partition("Prerequisite: ")
    prerequisites = string[2]
    
    return (prerequisites, restrictions, equivalences)

current_semester = get_semester(month)

if current_semester is "Spring":
    next_semester = "Summer"
elif current_semester is "Summer":
    next_semester = "Fall"
elif current_semester is "Fall":
    next_semester = "Winter"
elif current_semester is "Winter":
    next_semester = "Spring"

then = time.time()

print("Parsing majors...", end="")

majors = parse_between(requests.get(root_url).text, '<span class="prefix-abbrev push_one two columns">', '</span>')

print("done")

output_csv = open(output_csv, "w")
columns = ",".join(("Course ID", "Title", "Major", "Credits", "Grading Methods", "GenEd", "Prerequisites", "Restrictions", "Equivalences", "Description"))
print(columns, file=output_csv)

for major in majors:
    major_url = root_url + "/" + str(year) + semesters[semester] + "/" + major
    # get part of HTML relevant to course info and split into courses
    html_all_courses = requests.get(major_url).text.partition('<div class="courses-container">')[2].partition('<script type="text/javascript">')[0].split('<div id="')
    del html_all_courses[0]
    
    for html_single_course in html_all_courses:
        course_id = html_single_course.partition('" class="course">')[0]
        course_title = parse_between(html_single_course, '<span class="course-title">', '</span>')[0].replace('"', "'")
        course_min_credits = parse_between(html_single_course, '<span class="course-min-credits">', '</span>')[0]
        grading_method = ";".join(parse_between(parse_between(html_single_course, '<span class="grading-method">', '</span>')[0], '<abbr title="', '"><span>')[0].split(", "))
        course_subcategory = parse_between(parse_between(html_single_course, '<span class="course-subcategory">', '</span>')[0], '">', '</a>')[0]
        
        approved_course_text = parse_between(html_single_course, '<div class="approved-course-text">', '</div>')
        prerequisites, restrictions, equivalences = parse_course_info(approved_course_text[0])
        
        if len(approved_course_text) > 1:
            description = approved_course_text[1]
        else:
            description = approved_course_text[0]
            
        data = '"' + '","'.join((course_id, course_title, major, course_min_credits, grading_method, course_subcategory, prerequisites, restrictions, equivalences, description)) + '"'
        print(data, file=output_csv)

output_csv.close()

print("Parsing courses took " + str(int(time.time() - then)) + " seconds")