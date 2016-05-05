'''
Created on May 4, 2016

@author: Zach
'''
import requests, time, datetime

default_output_csv = "C:/Users/Zach/Desktop/courses.csv"
default_root_url = "https://ntst.umd.edu/soc"
semesters = {"Spring": "01", "Summer": "05", "Fall": "08", "Winter": "12"}

def get_semester(month):
    """Returns semester of given month number."""
    for semester in semesters:
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

def parse_courses_to_file(semester=current_semester, year=current_year, root_url=default_root_url, output_file=default_output_csv):
    """Write course data to file"""
    output_file = output_file.partition(".csv")[0] + "_" + semester + "_" + str(year) + ".csv"
    output_file = open(output_file, "w")
    print("Writing course data to " + output_file.name)
    print(parse_courses(semester, year, root_url), file=output_file)
    output_file.close()

def get_majors(root_url=default_root_url):
    """Returns list of majors parsed from main page."""
    return parse_between(requests.get(root_url).text, '<span class="prefix-abbrev push_one two columns">', '</span>')

def parse_courses(semester=current_semester, year=current_year, root_url=default_root_url):
    """Returns course data in CSV format for given semester and year"""
    then = time.time()
    print("Downloading course data for " + semester + " " + str(year) + " semester...")
    
    majors = get_majors(root_url)
    
    courses_csv = ",".join(("Course ID", "Title", "Major", "Credits", "Grading Methods", "GenEd", "Prerequisites", "Restrictions", "Equivalences", "Description")) + "\n"
    
    for major in majors:
        major_url = root_url + "/" + str(year) + semesters[semester] + "/" + major
        # get part of HTML relevant to course info and split into courses
        major_html = requests.get(major_url).text.partition('<div class="courses-container">')[2].partition('<script type="text/javascript">')[0].split('<div id="')
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
            courses_csv += '"' + '","'.join((course_id, course_title, major, course_min_credits, grading_methods, gen_ed_codes, prerequisites, restrictions, equivalences, description)) + '"' + "\n"
        
    print("Download complete, took " + str(int(time.time() - then)) + " seconds.")
    return courses_csv