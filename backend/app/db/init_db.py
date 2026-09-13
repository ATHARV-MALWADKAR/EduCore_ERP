"""
Comprehensive database initialization and seeding for College ERP.
Populates standard roles, admin/faculty/student users, departments, courses,
subjects, assignments, notices, and timetable entries.
"""
from datetime import date, datetime, time, timezone
from sqlalchemy.orm import Session
from app.db.models import (
    Role, User, Department, Course, Subject, Student, Faculty,
    Enrollment, Attendance, Assignment, Submission, Result, Notice, TimetableEntry
)
from app.core.security import hash_password


def init_roles(db: Session) -> dict[str, Role]:
    """Initialize default roles and return mapping."""
    role_data = {
        "admin": "Administrator with full system control and configuration privileges",
        "faculty": "Faculty member who manages courses, grades, attendance and assignments",
        "student": "Student enrolled in academic programs with access to grades and materials",
    }
    roles = {}
    for name, desc in role_data.items():
        role = db.query(Role).filter(Role.name == name).first()
        if not role:
            role = Role(name=name, description=desc)
            db.add(role)
            db.flush()
        roles[name] = role
    db.commit()
    return roles


def init_departments_and_courses(db: Session) -> tuple[dict[str, Department], dict[str, Course], list[Subject]]:
    """Create standard academic departments, degree programs, and curriculum."""
    # 1. Departments
    dept_specs = [
        ("Computer Science & Engineering", "CSE", "Core computing, AI, systems, and software engineering"),
        ("Electronics & Communication", "ECE", "Signal processing, VLSI, embedded systems, and telecommunication"),
        ("Mechanical Engineering", "MECH", "Thermodynamics, robotics, CAD/CAM, and materials engineering"),
        ("Business Administration", "MBA", "Finance, marketing, organizational leadership, and supply chain"),
    ]
    departments = {}
    for name, code, desc in dept_specs:
        dept = db.query(Department).filter(Department.code == code).first()
        if not dept:
            dept = Department(name=name, code=code, description=desc)
            db.add(dept)
            db.flush()
        departments[code] = dept

    # 2. Courses
    course_specs = [
        ("B.Tech in Computer Science", "BT-CSE", departments["CSE"].id, 4),
        ("M.Tech in Artificial Intelligence", "MT-AI", departments["CSE"].id, 2),
        ("B.Tech in Electronics & Comm.", "BT-ECE", departments["ECE"].id, 4),
        ("Master of Business Admin", "MBA-GEN", departments["MBA"].id, 2),
    ]
    courses = {}
    for name, code, dept_id, duration in course_specs:
        course = db.query(Course).filter(Course.code == code).first()
        if not course:
            course = Course(name=name, code=code, department_id=dept_id, duration_years=duration)
            db.add(course)
            db.flush()
        courses[code] = course

    # 3. Subjects
    subject_specs = [
        # Course, Name, Code, Sem, Credits
        ("BT-CSE", "Data Structures & Algorithms", "CS201", 3, 4.0),
        ("BT-CSE", "Database Management Systems", "CS301", 5, 4.0),
        ("BT-CSE", "Operating Systems", "CS302", 5, 3.5),
        ("BT-CSE", "Software Engineering & ERP", "CS401", 7, 3.0),
        ("BT-ECE", "Digital Signal Processing", "EC301", 5, 4.0),
        ("BT-ECE", "Microcontrollers & Embedded Systems", "EC302", 5, 4.0),
        ("MBA-GEN", "Financial Accounting & Analytics", "MB101", 1, 3.0),
        ("MBA-GEN", "Strategic Human Resource Management", "MB102", 1, 3.0),
    ]
    subjects = []
    for c_code, s_name, s_code, sem, creds in subject_specs:
        sub = db.query(Subject).filter(Subject.code == s_code, Subject.course_id == courses[c_code].id).first()
        if not sub:
            sub = Subject(
                name=s_name,
                code=s_code,
                course_id=courses[c_code].id,
                semester=sem,
                credits=creds
            )
            db.add(sub)
            db.flush()
        subjects.append(sub)

    db.commit()
    return departments, courses, subjects


def init_users_and_profiles(db: Session, roles: dict[str, Role], departments: dict[str, Department], courses: dict[str, Course]) -> tuple[User, list[Faculty], list[Student]]:
    """Seed administrator, faculty members, and student cohorts."""
    # 1. Admin
    admin_email = "admin@college.edu"
    admin = db.query(User).filter(User.email == admin_email).first()
    if not admin:
        admin = User(
            email=admin_email,
            full_name="System Administrator",
            hashed_password=hash_password("admin123"),
            role_id=roles["admin"].id,
            is_active=True
        )
        db.add(admin)
        db.flush()

    # 2. Faculty
    faculty_specs = [
        ("prof.alan@college.edu", "Prof. Alan Turing", "EMP1001", "CSE", "Professor & HoD"),
        ("prof.ada@college.edu", "Dr. Ada Lovelace", "EMP1002", "CSE", "Associate Professor"),
        ("prof.shannon@college.edu", "Prof. Claude Shannon", "EMP2001", "ECE", "Professor"),
        ("dr.drucker@college.edu", "Dr. Peter Drucker", "EMP3001", "MBA", "Professor & Dean"),
    ]
    faculty_list = []
    for email, name, emp_id, dept_code, desig in faculty_specs:
        u = db.query(User).filter(User.email == email).first()
        if not u:
            u = User(
                email=email,
                full_name=name,
                hashed_password=hash_password("faculty123"),
                role_id=roles["faculty"].id,
                is_active=True
            )
            db.add(u)
            db.flush()

        fac = db.query(Faculty).filter(Faculty.user_id == u.id).first()
        if not fac:
            fac = Faculty(
                user_id=u.id,
                employee_id=emp_id,
                department_id=departments[dept_code].id,
                designation=desig
            )
            db.add(fac)
            db.flush()
        faculty_list.append(fac)

    # 3. Students
    student_specs = [
        ("student.john@college.edu", "John Doe", "2024CS001", "CSE", "BT-CSE", "2024-2028"),
        ("student.jane@college.edu", "Jane Smith", "2024CS002", "CSE", "BT-CSE", "2024-2028"),
        ("student.alex@college.edu", "Alex Turner", "2024EC001", "ECE", "BT-ECE", "2024-2028"),
        ("student.sarah@college.edu", "Sarah Connor", "2025MB001", "MBA", "MBA-GEN", "2025-2027"),
    ]
    student_list = []
    for email, name, roll, dept_code, course_code, batch in student_specs:
        u = db.query(User).filter(User.email == email).first()
        if not u:
            u = User(
                email=email,
                full_name=name,
                hashed_password=hash_password("student123"),
                role_id=roles["student"].id,
                is_active=True
            )
            db.add(u)
            db.flush()

        stud = db.query(Student).filter(Student.user_id == u.id).first()
        if not stud:
            stud = Student(
                user_id=u.id,
                roll_number=roll,
                department_id=departments[dept_code].id,
                course_id=courses[course_code].id,
                batch=batch
            )
            db.add(stud)
            db.flush()
        student_list.append(stud)

    db.commit()
    return admin, faculty_list, student_list


def init_academic_operations(
    db: Session,
    admin: User,
    faculty_list: list[Faculty],
    student_list: list[Student],
    subjects: list[Subject],
    courses: dict[str, Course],
    departments: dict[str, Department]
) -> None:
    """Populate operational data: enrollments, timetable, attendance records, notices, assignments."""
    # 1. Enrollments
    for stud in student_list:
        existing_enroll = db.query(Enrollment).filter(
            Enrollment.student_id == stud.id,
            Enrollment.course_id == stud.course_id,
            Enrollment.academic_year == "2025-2026"
        ).first()
        if not existing_enroll:
            enroll = Enrollment(
                student_id=stud.id,
                course_id=stud.course_id,
                academic_year="2025-2026",
                enrolled_at=datetime.now(timezone.utc),
                status="active"
            )
            db.add(enroll)

    # 2. Notices
    notice_specs = [
        ("Welcome to Academic Year 2025-26", "Semester classes officially commence from Monday. Please verify your timetable and enrolled courses.", admin.id, "all", None),
        ("Mid-Term Examinations Schedule", "Mid-term examinations will be conducted in the first week of next month. Syllabus covers Modules 1 through 3.", faculty_list[0].user_id, "students", departments["CSE"].id),
        ("Faculty Research Grant Proposals", "Submit research proposals for university internal funding before the end of the quarter.", admin.id, "faculty", None),
    ]
    for title, content, author_id, audience, dept_id in notice_specs:
        if not db.query(Notice).filter(Notice.title == title).first():
            n = Notice(
                title=title,
                content=content,
                created_by_id=author_id,
                target_audience=audience,
                department_id=dept_id
            )
            db.add(n)

    # 3. Timetable
    cs_sub = subjects[0]  # DSA
    db_sub = subjects[1]  # DBMS
    timetable_specs = [
        ("BT-CSE", cs_sub.id, faculty_list[0].id, 1, time(9, 0), time(10, 0), "Lab-301", "2025-2026"),
        ("BT-CSE", cs_sub.id, faculty_list[0].id, 3, time(10, 0), time(11, 0), "Room-102", "2025-2026"),
        ("BT-CSE", db_sub.id, faculty_list[1].id, 2, time(11, 0), time(12, 0), "Lab-204", "2025-2026"),
        ("BT-CSE", db_sub.id, faculty_list[1].id, 4, time(14, 0), time(15, 0), "Room-105", "2025-2026"),
    ]
    for c_code, sub_id, fac_id, day, st, et, rm, yr in timetable_specs:
        existing_tt = db.query(TimetableEntry).filter(
            TimetableEntry.course_id == courses[c_code].id,
            TimetableEntry.subject_id == sub_id,
            TimetableEntry.day_of_week == day,
            TimetableEntry.academic_year == yr
        ).first()
        if not existing_tt:
            tt = TimetableEntry(
                course_id=courses[c_code].id,
                subject_id=sub_id,
                faculty_id=fac_id,
                day_of_week=day,
                start_time=st,
                end_time=et,
                room=rm,
                academic_year=yr
            )
            db.add(tt)

    # 4. Assignments
    asg = db.query(Assignment).filter(Assignment.title == "Project 1: Binary Search Tree Implementation").first()
    if not asg:
        asg = Assignment(
            subject_id=cs_sub.id,
            created_by_id=faculty_list[0].id,
            title="Project 1: Binary Search Tree Implementation",
            description="Implement an AVL Balanced Binary Search Tree in C++/Python with deletion & rotation logic.",
            due_at=datetime(2026, 10, 15, 23, 59, tzinfo=timezone.utc),
            status="published"
        )
        db.add(asg)
        db.flush()

    # 5. Sample Attendance
    for stud in student_list[:2]:  # CS students
        for day_offset in range(1, 5):
            rec_date = date(2026, 9, day_offset)
            existing_att = db.query(Attendance).filter(
                Attendance.student_id == stud.id,
                Attendance.subject_id == cs_sub.id,
                Attendance.date == rec_date
            ).first()
            if not existing_att:
                att = Attendance(
                    student_id=stud.id,
                    subject_id=cs_sub.id,
                    date=rec_date,
                    status="present" if (stud.id + day_offset) % 4 != 0 else "absent",
                    remarks="Regular lecture attendance"
                )
                db.add(att)

    db.commit()


def seed_database(db: Session) -> None:
    """Run master database seeding pipeline."""
    print("[*] Seeding College ERP database...")
    roles = init_roles(db)
    departments, courses, subjects = init_departments_and_courses(db)
    admin, faculty_list, student_list = init_users_and_profiles(db, roles, departments, courses)
    init_academic_operations(db, admin, faculty_list, student_list, subjects, courses, departments)
    print("[+] Seeding complete! Standard accounts ready:")
    print("    ADMIN:   admin@college.edu / admin123")
    print("    FACULTY: prof.alan@college.edu / faculty123")
    print("    STUDENT: student.john@college.edu / student123")
