"""
Seed generator — populates the database with realistic data for the
multi-tenant University AI dashboard.

- Tenants  : real universities of Telangana state, India.
- People   : students, professors, admins with authentic Telugu names + IDs.
- Academics: departments, programs, courses, sections, enrollments,
             attendance, assessments, marks.
- Finance  : invoices, payments, payroll runs, payslips, hall tickets, expenses.

Run:
    cd /app/backend && python seed_data.py

It drops & recreates all tables (SQLite dev DB by default) and exports CSV/JSON
samples to ./seed_output/ for quick inspection.
"""

import csv
import json
import os
import random
from datetime import date, datetime, timedelta, timezone

from app.database import Base, SessionLocal, engine
from app import models as m

random.seed(42)

# --------------------------------------------------------------------------- #
# Reference data
# --------------------------------------------------------------------------- #

UNIVERSITIES = [
    # (tenant_id/code, name, short_code, type, city, established)
    ("OU",    "Osmania University",                                        "OU",    "State",   "Hyderabad",   1918),
    ("JNTUH", "Jawaharlal Nehru Technological University Hyderabad",       "JNTUH", "State",   "Hyderabad",   1972),
    ("UOH",   "University of Hyderabad",                                   "UoH",   "Central", "Hyderabad",   1974),
    ("KU",    "Kakatiya University",                                       "KU",    "State",   "Warangal",    1976),
    ("TU",    "Telangana University",                                      "TU",    "State",   "Nizamabad",   2006),
    ("SU",    "Satavahana University",                                     "SU",    "State",   "Karimnagar",  2008),
    ("PU",    "Palamuru University",                                       "PU",    "State",   "Mahbubnagar", 2008),
    ("IIITH", "International Institute of Information Technology Hyderabad","IIIT-H","Deemed",  "Hyderabad",   1998),
]

TELUGU_MALE = [
    "Venkata", "Srinivas", "Ravi", "Kiran", "Praveen", "Rajesh", "Mahesh",
    "Naveen", "Sandeep", "Anil", "Suresh", "Vamshi", "Karthik", "Bhargav",
    "Sai", "Teja", "Rohith", "Akhil", "Charan", "Nikhil", "Sumanth", "Harish",
    "Manoj", "Pavan", "Vinay", "Aravind", "Deepak", "Vishnu", "Abhishek",
    "Yashwanth", "Rakesh", "Goutham", "Saketh", "Uday", "Chaitanya",
]

TELUGU_FEMALE = [
    "Lakshmi", "Sravani", "Divya", "Swapna", "Anusha", "Sahithi", "Keerthi",
    "Navya", "Bhavana", "Pooja", "Sneha", "Harika", "Spandana", "Madhavi",
    "Ramya", "Vaishnavi", "Aishwarya", "Nikitha", "Sushma", "Tejaswini",
    "Manasa", "Pranavi", "Akshaya", "Sindhu", "Varsha", "Meghana", "Sravya",
    "Deepika", "Haritha", "Sahasra", "Bhavya", "Lasya", "Nandini", "Sirisha",
]

SURNAMES = [
    "Reddy", "Rao", "Goud", "Naidu", "Yadav", "Sharma", "Chary", "Kumar",
    "Varma", "Mudiraj", "Bandi", "Bollam", "Kommu", "Gattu", "Mamidi",
    "Pittala", "Thota", "Vemula", "Kandula", "Bandari", "Cheruku", "Dasari",
    "Gandla", "Jakkula", "Mallepally", "Peddinti", "Sirikonda", "Nallamothu",
    "Madiraju", "Kasturi", "Pasula", "Eluri", "Ganta", "Anumula",
]

# (name, code, degree, sample courses [(code,title,sem)])
DEPARTMENTS = [
    ("Computer Science & Engineering", "CSE", "B.Tech", [
        ("CS201", "Data Structures", 3), ("CS202", "Database Management Systems", 3),
        ("CS301", "Operating Systems", 5), ("CS302", "Computer Networks", 5),
        ("CS401", "Machine Learning", 7), ("CS402", "Cloud Computing", 7),
    ]),
    ("Electronics & Communication Engineering", "ECE", "B.Tech", [
        ("EC201", "Electronic Devices", 3), ("EC202", "Digital Logic Design", 3),
        ("EC301", "Signals & Systems", 5), ("EC302", "Microprocessors", 5),
    ]),
    ("Electrical & Electronics Engineering", "EEE", "B.Tech", [
        ("EE201", "Circuit Theory", 3), ("EE301", "Power Systems", 5),
        ("EE302", "Control Systems", 5),
    ]),
    ("Mechanical Engineering", "MEC", "B.Tech", [
        ("ME201", "Thermodynamics", 3), ("ME301", "Fluid Mechanics", 5),
        ("ME302", "Machine Design", 5),
    ]),
    ("Civil Engineering", "CIV", "B.Tech", [
        ("CE201", "Surveying", 3), ("CE301", "Structural Analysis", 5),
    ]),
    ("Business Administration", "MBA", "MBA", [
        ("MB101", "Principles of Management", 1), ("MB201", "Marketing Management", 3),
        ("MB202", "Financial Management", 3),
    ]),
    ("Pharmacy", "PHA", "B.Pharm", [
        ("PH201", "Pharmaceutical Chemistry", 3), ("PH301", "Pharmacology", 5),
    ]),
]

DESIGNATIONS = ["Assistant Professor", "Associate Professor", "Professor", "HOD"]
SPECIALIZATIONS = [
    "Artificial Intelligence", "Data Science", "VLSI Design", "Power Electronics",
    "Thermal Engineering", "Structural Engineering", "Finance", "Pharmacology",
    "Computer Networks", "Embedded Systems", "Marketing",
]
ADMIN_ROLES = [
    ("Registrar", "Administration"),
    ("Accounts Officer", "Accounts"),
    ("Examination Controller", "Examinations"),
    ("Finance Manager", "Accounts"),
    ("Admissions Officer", "Administration"),
]
EXPENSE_CATEGORIES = ["Infrastructure", "Salaries", "Utilities", "Events", "Library", "Laboratory"]
PAYMENT_METHODS = ["UPI", "Card", "NetBanking", "Cash"]

ACADEMIC_YEAR = "2025-26"


def full_name():
    gender = random.choice(["Male", "Female"])
    first = random.choice(TELUGU_MALE if gender == "Male" else TELUGU_FEMALE)
    last = random.choice(SURNAMES)
    return f"{first} {last}", first, last, gender


def email_for(first, last, domain, salt):
    return f"{first.lower()}.{last.lower()}{salt}@{domain}"


def phone():
    return "9" + "".join(random.choice("0123456789") for _ in range(9))


def rand_date(start_year, end_year):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 28)
    return start + timedelta(days=random.randint(0, (end - start).days))


# --------------------------------------------------------------------------- #
# Generation
# --------------------------------------------------------------------------- #

def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    counters = {k: 0 for k in [
        "universities", "departments", "programs", "professors", "admins",
        "students", "courses", "sections", "enrollments", "attendance",
        "assessments", "marks", "invoices", "payments", "payslips",
        "halltickets", "expenses",
    ]}

    for code, name, short, utype, city, est in UNIVERSITIES:
        domain = f"{code.lower()}.ac.in"
        uni = m.University(
            tenant_id=code, name=name, short_code=short, university_type=utype,
            city=city, established_year=est, portal_url=f"https://{domain}",
            ai_enabled=random.choice([True, True, False]),
        )
        db.add(uni)
        counters["universities"] += 1

        # Departments for this university (random subset of 4-7)
        dept_defs = random.sample(DEPARTMENTS, k=random.randint(4, min(7, len(DEPARTMENTS))))
        dept_objs = []
        prof_pool_by_dept = {}

        fac_seq = 1000
        adm_seq = 1
        roll_seq_by_dept = {}

        for dname, dcode, degree, courses in dept_defs:
            dept = m.Department(tenant_id=code, name=dname, code=dcode)
            db.add(dept)
            db.flush()
            dept_objs.append((dept, dcode, degree, courses))
            counters["departments"] += 1
            roll_seq_by_dept[dept.id] = 1

            program = m.Program(
                tenant_id=code, department_id=dept.id,
                name=f"{degree} {dname}", degree=degree,
                duration_years=2 if degree in ("MBA", "M.Tech", "M.Sc") else 4,
            )
            db.add(program)
            db.flush()
            counters["programs"] += 1
            dept.program_id = program.id  # convenience handle

            # Professors (2-4 per dept)
            profs = []
            for _ in range(random.randint(2, 4)):
                fac_seq += 1
                fname, fi, fl, gender = full_name()
                user = m.User(
                    tenant_id=code, full_name=fname,
                    email=email_for(fi, fl, domain, fac_seq), role="professor",
                    gender=gender, phone=phone(),
                    auth_type=random.choice(["local", "sso"]),
                )
                db.add(user)
                db.flush()
                prof = m.ProfessorProfile(
                    tenant_id=code, user_id=user.id,
                    employee_id=f"{code}-FAC-{fac_seq}", department_id=dept.id,
                    designation=random.choice(DESIGNATIONS),
                    specialization=random.choice(SPECIALIZATIONS),
                    date_of_joining=rand_date(2008, 2023),
                    monthly_salary=round(random.uniform(60000, 180000), -2),
                )
                db.add(prof)
                db.flush()
                profs.append(prof)
                counters["professors"] += 1
            prof_pool_by_dept[dept.id] = profs

            # Courses + sections for this dept
            for ccode, ctitle, csem in courses:
                course = m.Course(
                    tenant_id=code, department_id=dept.id,
                    professor_id=random.choice(profs).id,
                    code=ccode, title=ctitle, credits=random.choice([3, 4]),
                    semester=csem,
                )
                db.add(course)
                db.flush()
                counters["courses"] += 1
                section = m.Section(
                    tenant_id=code, course_id=course.id, name="A",
                    academic_year=ACADEMIC_YEAR, term=f"Sem-{csem}",
                )
                db.add(section)
                db.flush()
                counters["sections"] += 1
                dept_sections = prof_pool_by_dept  # placeholder, sections tracked below
                course._section = section  # attach for later enrollment

            # Students for this dept (15-35)
            dept_students = []
            for _ in range(random.randint(15, 35)):
                seq = roll_seq_by_dept[dept.id]
                roll_seq_by_dept[dept.id] += 1
                batch = random.choice([2022, 2023, 2024])
                roll = f"{code}{str(batch)[2:]}{dcode}{seq:03d}"
                fname, fi, fl, gender = full_name()
                user = m.User(
                    tenant_id=code, full_name=fname,
                    email=email_for(fi, fl, domain, roll.lower()), role="student",
                    gender=gender, phone=phone(),
                    auth_type=random.choice(["local", "sso"]),
                )
                db.add(user)
                db.flush()
                year = 2025 - batch + 1
                student = m.StudentProfile(
                    tenant_id=code, user_id=user.id, roll_no=roll,
                    department_id=dept.id, program_id=program.id,
                    batch_year=batch, current_year=max(1, min(4, year)),
                    current_semester=max(1, min(8, year * 2 - random.randint(0, 1))),
                    cgpa=round(random.uniform(5.5, 9.8), 2),
                    date_of_birth=rand_date(2002, 2006),
                )
                db.add(student)
                db.flush()
                dept_students.append(student)
                counters["students"] += 1

            db.flush()

            # Enrollments + attendance + assessments + marks
            dept_courses = [c for c in db.new if isinstance(c, m.Course)]  # not reliable; query instead
            sections = db.query(m.Section).join(
                m.Course, m.Course.id == m.Section.course_id
            ).filter(m.Course.department_id == dept.id).all()

            for student in dept_students:
                chosen = random.sample(sections, k=min(len(sections), random.randint(3, 5)))
                for section in chosen:
                    db.add(m.Enrollment(
                        tenant_id=code, section_id=section.id, student_id=student.id,
                    ))
                    counters["enrollments"] += 1
                    # Attendance: 8 class dates
                    base = date(2025, 8, 1)
                    for w in range(8):
                        cdate = base + timedelta(days=w * 7)
                        status = random.choices(
                            ["present", "absent", "late"], weights=[80, 15, 5]
                        )[0]
                        db.add(m.AttendanceRecord(
                            tenant_id=code, section_id=section.id,
                            student_id=student.id, class_date=cdate, status=status,
                        ))
                        counters["attendance"] += 1

            # Assessments per section + marks for enrolled students
            for section in sections:
                assessments = []
                for atype, mx, wt, d in [
                    ("Mid-1", 30, 25, date(2025, 9, 15)),
                    ("Mid-2", 30, 25, date(2025, 11, 10)),
                    ("Final", 70, 50, date(2025, 12, 20)),
                ]:
                    a = m.Assessment(
                        tenant_id=code, section_id=section.id, type=atype,
                        max_marks=mx, weightage=wt, held_on=d,
                    )
                    db.add(a)
                    db.flush()
                    assessments.append(a)
                    counters["assessments"] += 1
                enrolled = db.query(m.Enrollment).filter(
                    m.Enrollment.section_id == section.id
                ).all()
                for enr in enrolled:
                    for a in assessments:
                        score = round(random.uniform(0.4, 1.0) * a.max_marks, 1)
                        db.add(m.Mark(
                            tenant_id=code, assessment_id=a.id,
                            student_id=enr.student_id, score=score,
                        ))
                        counters["marks"] += 1

        # --- Admins (3-5 per university) ---
        for i in range(random.randint(3, 5)):
            desig, office = random.choice(ADMIN_ROLES)
            fname, fi, fl, gender = full_name()
            user = m.User(
                tenant_id=code, full_name=fname,
                email=email_for(fi, fl, domain, f"adm{adm_seq}"), role="admin",
                gender=gender, phone=phone(), auth_type="local",
            )
            db.add(user)
            db.flush()
            db.add(m.AdminProfile(
                tenant_id=code, user_id=user.id,
                employee_id=f"{code}-ADM-{adm_seq:03d}", designation=desig,
                office=office, date_of_joining=rand_date(2010, 2022),
            ))
            adm_seq += 1
            counters["admins"] += 1

        db.flush()

        # --- Finance: invoices + payments + hall tickets per student ---
        students = db.query(m.StudentProfile).filter(
            m.StudentProfile.tenant_id == code
        ).all()
        for student in students:
            amount = random.choice([45000, 60000, 75000, 90000, 120000])
            status = random.choices(["paid", "unpaid", "partial", "overdue"],
                                    weights=[55, 20, 15, 10])[0]
            inv = m.Invoice(
                tenant_id=code, student_id=student.id,
                description=f"Tuition Fee {ACADEMIC_YEAR}", amount=amount,
                status=status, due_date=date(2025, 9, 30),
            )
            db.add(inv)
            db.flush()
            counters["invoices"] += 1
            if status in ("paid", "partial"):
                pay_amt = amount if status == "paid" else round(amount * 0.5)
                db.add(m.Payment(
                    tenant_id=code, invoice_id=inv.id, amount=pay_amt,
                    method=random.choice(PAYMENT_METHODS),
                    provider_ref=f"TXN{random.randint(10**9, 10**10)}",
                    status="success",
                ))
                counters["payments"] += 1
            # Hall ticket eligibility: blocked if overdue fee
            blocked = status in ("unpaid", "overdue") and random.random() < 0.5
            db.add(m.HallTicket(
                tenant_id=code, student_id=student.id,
                exam_name=f"Sem End Exams {ACADEMIC_YEAR}",
                eligibility="blocked" if blocked else "eligible",
                block_reason="Pending fee payment" if blocked else None,
                issued_at=datetime.now(timezone.utc) if not blocked else None,
            ))
            counters["halltickets"] += 1

        # --- Payroll for professors ---
        run = m.PayrollRun(tenant_id=code, period="2026-05", status="completed")
        db.add(run)
        db.flush()
        for prof in db.query(m.ProfessorProfile).filter(
            m.ProfessorProfile.tenant_id == code
        ).all():
            gross = prof.monthly_salary or 80000
            deductions = round(gross * random.uniform(0.08, 0.15), 2)
            db.add(m.Payslip(
                tenant_id=code, payroll_run_id=run.id, professor_id=prof.id,
                gross=gross, deductions=deductions, net=round(gross - deductions, 2),
            ))
            counters["payslips"] += 1

        # --- Expenses ---
        for _ in range(random.randint(8, 15)):
            db.add(m.Expense(
                tenant_id=code, category=random.choice(EXPENSE_CATEGORIES),
                description="Operational expense",
                amount=round(random.uniform(50000, 2500000), -2),
                vendor=random.choice(["L&T", "Tata Projects", "BSNL", "TSSPDCL",
                                      "Local Vendor", "Cengage", "Dell India"]),
                spent_on=rand_date(2025, 2026),
            ))
            counters["expenses"] += 1

        # Audit trail example
        m.log_event(db, code, m.EventType.TENANT_CREATED, f"Seeded {name}")
        if uni.ai_enabled:
            m.log_event(db, code, m.EventType.AI_ENABLED, "AI enabled at seed time")

        db.commit()
        print(f"  seeded {name}")

    export_samples(db)
    db.close()

    print("\n=== SEED SUMMARY ===")
    for k, v in counters.items():
        print(f"  {k:14s}: {v}")


def export_samples(db):
    out = os.path.join(os.path.dirname(__file__), "seed_output")
    os.makedirs(out, exist_ok=True)

    # Universities CSV
    with open(os.path.join(out, "universities.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tenant_id", "name", "type", "city", "established", "ai_enabled"])
        for u in db.query(m.University).all():
            w.writerow([u.tenant_id, u.name, u.university_type, u.city,
                        u.established_year, u.ai_enabled])

    # Students sample CSV (first 60)
    with open(os.path.join(out, "students_sample.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["roll_no", "name", "email", "tenant", "batch", "year", "cgpa"])
        rows = db.query(m.StudentProfile).limit(60).all()
        for s in rows:
            u = db.query(m.User).get(s.user_id)
            w.writerow([s.roll_no, u.full_name, u.email, s.tenant_id,
                        s.batch_year, s.current_year, s.cgpa])

    # Professors sample CSV
    with open(os.path.join(out, "professors_sample.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["employee_id", "name", "email", "tenant", "designation", "specialization", "salary"])
        for p in db.query(m.ProfessorProfile).limit(60).all():
            u = db.query(m.User).get(p.user_id)
            w.writerow([p.employee_id, u.full_name, u.email, p.tenant_id,
                        p.designation, p.specialization, p.monthly_salary])

    # Admins CSV
    with open(os.path.join(out, "admins.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["employee_id", "name", "email", "tenant", "designation", "office"])
        for a in db.query(m.AdminProfile).all():
            u = db.query(m.User).get(a.user_id)
            w.writerow([a.employee_id, u.full_name, u.email, a.tenant_id,
                        a.designation, a.office])

    # JSON: one full student record with relations
    s = db.query(m.StudentProfile).first()
    u = db.query(m.User).get(s.user_id)
    dept = db.query(m.Department).get(s.department_id)
    sample = {
        "student": {
            "roll_no": s.roll_no, "name": u.full_name, "email": u.email,
            "tenant_id": s.tenant_id, "department": dept.name,
            "batch_year": s.batch_year, "cgpa": s.cgpa,
        }
    }
    with open(os.path.join(out, "sample_student.json"), "w") as f:
        json.dump(sample, f, indent=2)

    print(f"\nExported CSV/JSON samples to: {out}")


if __name__ == "__main__":
    seed()
