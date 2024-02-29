import pymongo
import yaml

# Load configuration from a YAML file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Connect to MongoDB
client = pymongo.MongoClient(config["mongodb"]["uri"])
db = client[config["mongodb"]["database"]]
teachers_collection = db["teachers"]

# Function to insert sample teacher constraints data into MongoDB
def insert_sample_teachers(sample_teachers):
    teachers_collection.insert_many(sample_teachers)

# Function to retrieve teacher constraints from MongoDB
def get_teacher_constraints():
    return teachers_collection.find()

# Function to allocate teachers to slots based on constraints
def allocate_teachers_to_slots(teacher_constraints):
    time_ranges = ["7-11", "11-14", "14-18", "18-22"]
    schedule = {time_range: {} for time_range in time_ranges}

    for teacher in teacher_constraints:
        max_hours_lecture = teacher["max_hours_lecture"]
        preferred_time_ranges_lecture = teacher["preferred_time_ranges_lecture"]
        max_hours_practical = teacher["max_hours_practical"]
        preferred_time_ranges_practical = teacher["preferred_time_ranges_practical"]

        for time_range in preferred_time_ranges_lecture:
            if teacher["name"] not in schedule[time_range]:
                schedule[time_range][teacher["name"]] = "Lecture"
                max_hours_lecture -= 1
                if max_hours_lecture == 0:
                    break

        for time_range in preferred_time_ranges_practical:
            if teacher["name"] not in schedule[time_range]:
                schedule[time_range][teacher["name"]] = "Practical"
                max_hours_practical -= 1
                if max_hours_practical == 0:
                    break

    for time_range, teachers in schedule.items():
        for teacher in teachers_collection.find({"name": {"$nin": list(teachers.keys())}}):
            schedule[time_range][teacher["name"]] = "Allocated"

    return schedule

# Function to print the schedule
def print_schedule(schedule):
    print("Teacher Schedule:")
    for time_range, teachers in schedule.items():
        print(f"{time_range}:")
        for teacher, status in teachers.items():
            print(f"  - {teacher}: {status}")

# Insert sample teacher constraints data into MongoDB
sample_teachers = [
    {"name": "A", "max_hours_lecture": 4, "preferred_time_ranges_lecture": ["7-11", "11-14"], "max_hours_practical": 2, "preferred_time_ranges_practical": ["14-18"]},
    {"name": "B", "max_hours_lecture": 5, "preferred_time_ranges_lecture": ["7-11"], "max_hours_practical": 3, "preferred_time_ranges_practical": ["11-14"]},
    {"name": "C", "max_hours_lecture": 3, "preferred_time_ranges_lecture": ["11-14"], "max_hours_practical": 2, "preferred_time_ranges_practical": ["14-18"]},
    {"name": "D", "max_hours_lecture": 4, "preferred_time_ranges_lecture": ["18-22"], "max_hours_practical": 1, "preferred_time_ranges_practical": ["14-18"]}
]
insert_sample_teachers(sample_teachers)

# Retrieve teacher constraints from MongoDB
teacher_constraints = get_teacher_constraints()

# Allocate teachers to slots based on constraints
schedule = allocate_teachers_to_slots(teacher_constraints)

# Print the schedule
print_schedule(schedule)
