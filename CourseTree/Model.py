'''
Created on May 4, 2016

@author: Zach
'''
import CourseTree

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
    
    def __str__(self):
        return self.course_id + " " + self.course_title + "\n" + "Major: " + self.major + "\n" + "Credits: " + self.min_credits + "\n" + "Grading methods: " + str(self.grading_methods) + "\n" + "GenEd: " + str(self.gen_ed_codes) + "\n" + "Prerequisites: " + str(self.prerequisites) + "\n" + "Restrictions: " + str(self.restrictions) + "\n" + "Equivalences: " + str(self.equivalences) + "\n" + "Description: " + self.description
    
def get_courses(semester, year):
    """Returns list of Course objects parsed from main page"""
    input_csv = CourseTree.Input.parse_courses(semester=semester, year=year).split("\n")
    columns = input_csv[0].strip("\n").split(",")
    del input_csv[0]
    
    courses = []
    for line in input_csv:
        values = line.strip("\n").strip('"').split('","')
        course_id, course_title, major, course_min_credits, grading_methods, course_subcategory, prerequisites, restrictions, equivalences, description = values
        course = Course(course_id, course_title, major, course_min_credits, grading_methods, course_subcategory, prerequisites, restrictions, equivalences, description)
        print(course, end="\n\n")
        courses.append(course)
    
    return courses