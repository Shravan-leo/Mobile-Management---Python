import pandas as pd
from pip._internal.commands import index

employees = {
    "EmpId": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
    "Name": ["Ravi", "Sita", "Kiran", "Rahul", "Priya", "Anil", "OG", "Sachin", "Dhoni", "Sehwag" ],
    "Department": ["IT", "HR", "IT", "Sales", "HR", "IT", "ALL ROUNDER", "SPORT", "SPORT", "SPORT"],
    "Salary": [50000, 45000, 70000, 40000, 48000, 65000, 100000, 120000, 140000, 200000],
    "Experience": [2, 5, 8, 1, 4, 7, 25, 10, 7, 44 ]
}
# reading the data using pandas
df = pd.DataFrame(employees)
print(df.to_string(index=False))

# writing the data using pandas to csv file

df.to_csv("employees_data.csv",index=False)
print("*"*100)

# reading the data using pandas from csv file

print(pd.read_csv("employees_data.csv").to_string(index = False))
print("*"*100)

# writing the data using pandas to excel file

df.to_excel("employees_data.xlsx",index=False)

# reading the data using pandas from csv file
print(pd.read_excel("employees_data.xlsx").to_string(index = False))

# Important functions
print("******************head()***************")
print(df.head()) # default first 5 values
print("******************head(3)***************")
print(df.head(3)) # first 3 values
print("******************tail()***************")
print(df.tail()) # default last 5 values
print("******************tail(4)***************")
print(df.tail(4))# last 4 values
print("******************info()***************")
print(df.info())
print("******************describe()***************")
print(df.describe())

print(df["Name"])
print(df[["Name", "Salary"]])

# Assignment 1

students = {
    "Name":["Ravi","Sita","Kiran","Rahul","Priya"],
    "Course":["Python","Java","Python","DevOps","Python"],
    "Marks":[85,90,75,60,95]
}

df = pd.DataFrame(students)

# 1.Show only python students
print("******************Show only python students***************")
print(df[df["Course"] == "Python"])

# 2.Show students with marks > 80
print("******************Show students with marks > 80***************")
print(df[df["Marks"] > 80])

# 3.Sort students based on marks
print("******************Sort students based on marks***************")
print(df.sort_values("Marks"))

# 4.Find Highest marks
print("******************Find Highest marks using head***************")
sort = df.sort_values("Marks", ascending=False)
print(sort.head(1))  # using ascending and head
print("******************Find Highest marks using tail***************")
sort = df.sort_values("Marks")
print(sort.tail(1)) # using descending and tail

print("******************Find Highest marks using max***************")
print(df["Marks"].max())

print("******************Find Avg marks ***************")
print(df["Marks"].mean())

print("******************Count students in each course***************")
course_counts = df["Course"].value_counts().reset_index()
course_counts.columns = ["Course", "Student Count"]

print(course_counts.to_string(index=False))

print("******************Add Grade Column***************")

# Add Grade column
#df["Grade"]  = ""
#df["Grade"]  = 0
df.insert(1,"Grade",None)
print(df.to_string(index=False))

