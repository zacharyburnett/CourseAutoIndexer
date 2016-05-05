'''
Created on May 4, 2016

@author: Zach
'''

import CourseTree, datetime, os

years = range(2014, datetime.datetime.now().year + 1)
root_directory = "C:/Users/Zach/Desktop/courses"

print("Writing HTML for course data in range.")

for year in years:
    for semester in CourseTree.Input.semesters:
        print(semester + str(year) + " semester")
        for course in CourseTree.Model.get_courses(semester, year):
            print(course.course_id, end="")
            path = root_directory + "/" + course.major + "/" + course.course_id
            directory = os.path.dirname(path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            index_html = open(path + "/index.html", "w")
            
            course_html = "<!DOCTYPE=html>" + "\n" + "<html>" + "\n" + "<head>" + "\n" + "<title>" + course.course_id + "</title>" + "\n" + "</head>" + "\n" + "<body>" + "\n" + "<pre>" + "\n" + str(course) + "\n" + "</pre>" + "\n" + "</body>" + "\n" + "</html>"
            print(course_html, file=index_html)
        print()