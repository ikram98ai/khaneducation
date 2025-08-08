import json

SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Biology", "Computer Science"]

LANGUAGES = ["Arabic", "English", "Pashto", "Persian", "Urdu"] 

GRADES = list(range(1, 13))

LESSONS = {
    "Mathematics": {
        "easy": [
            "Counting Numbers 1-10", 
            "Adding Small Numbers", 
            "Subtracting Small Numbers", 
            "Basic Shapes Recognition", 
            "Measuring Length", 
            "Number Patterns", 
            "Telling Time", 
            "Counting Money", 
            "Simple Graphs", 
            "Basic Word Problems"
        ],
        "medium": [
            "Fractions and Decimals", 
            "Multiplication Tables", 
            "Basic Geometry", 
            "Area and Perimeter", 
            "Multi-step Word Problems", 
            "Data Analysis", 
            "Introduction to Algebra", 
            "Angles and Triangles", 
            "Basic Statistics", 
            "Coordinate Plane"
        ],
        "hard": [
            "Linear Equations", 
            "Quadratic Functions", 
            "Trigonometry Basics", 
            "Calculus Introduction", 
            "Probability Theory", 
            "Vector Mathematics", 
            "Matrix Operations", 
            "Logarithmic Functions", 
            "Geometric Series", 
            "Mathematical Proofs"
        ]
    },
    "Physics": {
        "easy": [
            "What is Motion?", 
            "Push and Pull Forces", 
            "Floating and Sinking", 
            "Light and Shadows", 
            "Sound Around Us", 
            "Magnets and Metals", 
            "Weather and Seasons", 
            "Simple Machines", 
            "Energy Sources", 
            "Basic Measurements"
        ],
        "medium": [
            "Speed and Velocity", 
            "Newton's Laws", 
            "Heat and Temperature", 
            "Electric Circuits", 
            "Reflection and Refraction", 
            "Work and Energy", 
            "Pressure in Fluids", 
            "Wave Properties", 
            "Simple Harmonic Motion", 
            "Basic Optics"
        ],
        "hard": [
            "Mechanics Dynamics", 
            "Electromagnetic Theory", 
            "Thermodynamics", 
            "Modern Physics", 
            "Quantum Concepts", 
            "Relativity Basics", 
            "Nuclear Physics", 
            "Fluid Mechanics", 
            "Oscillations", 
            "Advanced Optics"
        ]
    },
    "Chemistry": {
        "easy": [
            "Matter and Materials", 
            "States of Matter", 
            "Mixing Substances", 
            "Safe Laboratory Practices", 
            "Observing Changes", 
            "Air and Water", 
            "Rocks and Minerals", 
            "Everyday Chemicals", 
            "Sorting Materials", 
            "Basic Experiments"
        ],
        "medium": [
            "Atomic Structure", 
            "Periodic Table", 
            "Chemical Bonds", 
            "Chemical Reactions", 
            "Acids and Bases", 
            "Solutions and Solubility", 
            "Rates of Reaction", 
            "Energy Changes", 
            "Carbon Chemistry", 
            "Environmental Chemistry"
        ],
        "hard": [
            "Quantum Chemistry", 
            "Thermodynamics", 
            "Chemical Equilibrium", 
            "Electrochemistry", 
            "Organic Reactions", 
            "Analytical Chemistry", 
            "Biochemistry Basics", 
            "Industrial Chemistry", 
            "Polymer Chemistry", 
            "Nuclear Chemistry"
        ]
    },
    "Biology": {
        "easy": [
            "Living Things", 
            "Plant Parts", 
            "Animal Habitats", 
            "Human Body Systems", 
            "Food Chains", 
            "Life Cycles", 
            "Healthy Living", 
            "Plant Growth", 
            "Animal Adaptations", 
            "Basic Ecology"
        ],
        "medium": [
            "Cell Structure", 
            "Genetics Basics", 
            "Photosynthesis", 
            "Respiration", 
            "Ecosystems", 
            "Evolution", 
            "Microorganisms", 
            "Human Physiology", 
            "Biotechnology", 
            "Conservation"
        ],
        "hard": [
            "Molecular Biology", 
            "Genetic Engineering", 
            "Cellular Respiration", 
            "Protein Synthesis", 
            "Population Genetics", 
            "Ecological Systems", 
            "Immunology", 
            "Neuroscience", 
            "Biotechnology Applications", 
            "Advanced Genetics"
        ]
    },
    "Computer Science": {
        "easy": [
            "Introduction to Computers", 
            "Digital Citizenship", 
            "Basic Typing Skills", 
            "File Management", 
            "Internet Safety", 
            "Block Programming", 
            "Simple Animations", 
            "Digital Art", 
            "Online Collaboration", 
            "Problem Solving"
        ],
        "medium": [
            "Programming Basics", 
            "Variables and Loops", 
            "Conditional Statements", 
            "Functions", 
            "Data Types", 
            "User Interfaces", 
            "Debugging Skills", 
            "Simple Games", 
            "Web Pages", 
            "Database Concepts"
        ],
        "hard": [
            "Object-Oriented Programming", 
            "Data Structures", 
            "Algorithm Design", 
            "Software Engineering", 
            "Database Management", 
            "Network Security", 
            "Artificial Intelligence", 
            "Mobile Development", 
            "Cloud Computing", 
            "Capstone Project"
        ]
    }
}

USERS = [
        {
            "username": "shoukat",
            "email": "shoukat@edu.com",
            "password": "Aa12345.",
            "role": "student"
        },
        {
            "username": "basharat",
            "email": "basharat@edu.com",
            "password": "Aa12345.",
            "role": "student"
        },
        {
            "username": "hamdullah",
            "email": "hamdullah@edu.com",
            "password": "Aa12345.",
            "role": "student"
        },
        {
            "username": "qaseem",
            "email": "qaseem@edu.com",
            "password": "Aa12345.",
            "role": "student"
        },
        {
            "username": "inam",
            "email": "inam@edu.com",
            "password": "Aa12345.",
            "role": "student"
        },
        {
            "username": "zain",
            "email": "zain@edu.com",
            "password": "Aa12345.",
            "role": "student"
        },
        {
            "username": "waseem",
            "email": "waseem@edu.com",
            "password": "Aa12345.",
            "role": "student"
        },
        {
            "username": "ikramkhan",
            "email": "ikramk@edu.com",
            "password": "Aa12345.",
            "role": "admin"
        },
        {
            "username": "ikram98ai",
            "email": "ikram98ai@edu.com",
            "password": "Aa12345.",
            "role": "admin"
        }
    ]

def generate_data():
    subjects = []
    lessons = []
    
    for grade in GRADES:
        # Set difficulty band
        if grade <= 4: 
            diff_band = "easy"
        elif grade <= 8: 
            diff_band = "medium"
        else: 
            diff_band = "hard"
        
        for subject in SUBJECTS:
            
            for order in range(1, 11):
                for lang in LANGUAGES:
                    lesson = LESSONS[subject][diff_band][order-1]
                    
                    lessons.append({
                        "title": lesson,
                        "language": lang,
                        "content": f"Grade {grade} {subject}; Lesson {order}: {lesson}" ,
                        "difficulty": diff_band,
                        "order_in_subject": order
                    })
            subjects.append({
                "name": subject,
                "description": f"{subject} curriculum for Grade {grade}",
                "grade_level": grade,
                "is_active": True,
                "lessons": lessons
            
            })

        
    return {"users":USERS,"subjects": subjects}

# Generate and save data
if __name__ == "__main__":
    data = generate_data()
    with open("seed.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Generated curriculum data for {len(GRADES)} grades, {len(SUBJECTS)} subjects, and {len(LANGUAGES)} languages")
    print(f"Total subjects: {len(data['subjects'])}")
    print(f"Total lessons: {len(GRADES)*len(SUBJECTS)*len(LANGUAGES)}")
    print("Data saved to seed.json")
