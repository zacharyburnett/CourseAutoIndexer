'''
Created on May 4, 2016

@author: Zach
'''

input_csv = "C:/Users/Zach/Desktop/classes.csv"

courses = []

class Course:
    """Course with major, id, course_title, credits, grading_method methods, GenEd course_subcategory, prerequisites, and description."""
    def __init__(self, major, course_id, course_title, course_min_credits, grading_method, course_subcategory, prerequisites, restrictions, equivalences, description):
        self.major = major
        self.id = course_id
        self.title = course_title
        self.min_credits = course_min_credits
        self.grading_method = grading_method
        self.course_subcategory = course_subcategory
        self.prerequisites = prerequisites
        self.restrictions = restrictions
        self.equivalences = equivalences
        self.description = description
    
    def __str__(self):
        return self.id + " " + self.title + "\n" + "Major: " + self.major + "\n" + "Credits: " + self.min_credits + "\n" + "Grading methods: " + str(self.grading_method) + "\n" + "GenEd: " + self.course_subcategory + "\n" + "Prerequisites: " + str(self.prerequisites) + "\n" + "Restrictions: " + str(self.restrictions) + "\n" + "Equivalences: " + str(self.equivalences) + "\n" + "Description: " + self.description
    
input_csv = open(input_csv, "r").read()

