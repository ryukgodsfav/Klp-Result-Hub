"""
Main public-facing routes for the KLP Roorkee website.
Handles: Home page, About, Departments, Sports, Courses, and Contact.
"""

from flask import Blueprint, render_template

# Blueprint for all public pages
main_bp = Blueprint('main', __name__)


# ─── Home Page ────────────────────────────────────────────────────────────────

@main_bp.route('/')
def home():
    """Render the main landing page with college info, departments, hiring partners, etc."""

    # Hiring partner companies (displayed in a slider on the homepage)
    hiring_partners = [
        {"name": "TATA Group", "sector": "Manufacturing & Engineering"},
        {"name": "Maruti Suzuki", "sector": "Automobile"},
        {"name": "HCL Technologies", "sector": "Information Technology"},
        {"name": "Hero MotoCorp", "sector": "Automobile"},
        {"name": "Saraswati Dynamic Ltd.", "sector": "Engineering"},
        {"name": "Simple Infrastructure", "sector": "Construction"},
        {"name": "Lloyd Insulation Ltd.", "sector": "Insulation & Construction"},
        {"name": "Bajaj Auto", "sector": "Automobile"},
        {"name": "Kirby Building Systems", "sector": "Steel Buildings"},
        {"name": "ABB Ltd.", "sector": "Electrical & Automation"},
        {"name": "Kenwood", "sector": "Electronics"},
        {"name": "VIP Luggage Ltd.", "sector": "Manufacturing"},
        {"name": "TVS Ltd.", "sector": "Automobile"},
    ]

    # Department list with descriptions
    departments = [
        {
            "name": "Civil Engineering",
            "code": "CE",
            "icon": "🏗️",
            "desc": "Construction, structural design, and infrastructure development.",
            "seats": 60
        },
        {
            "name": "Mechanical Engineering",
            "code": "ME",
            "icon": "⚙️",
            "desc": "Machines, thermodynamics, manufacturing, and industrial processes.",
            "seats": 60
        },
        {
            "name": "Electrical Engineering",
            "code": "EE",
            "icon": "⚡",
            "desc": "Power systems, circuits, motors, and electrical installation.",
            "seats": 60
        },
        {
            "name": "Electronics Engineering",
            "code": "EN",
            "icon": "📡",
            "desc": "Electronic circuits, communication systems, and embedded tech.",
            "seats": 60
        },
        {
            "name": "AI & Machine Learning",
            "code": "AIML",
            "icon": "🤖",
            "desc": "Artificial intelligence, data science, and machine learning applications.",
            "seats": 60
        },
        {
            "name": "Computer Communication & Networking",
            "code": "CCN",
            "icon": "🌐",
            "desc": "Networking protocols, cybersecurity, and IT infrastructure.",
            "seats": 60
        },
    ]

    # Sports events / activities at KLP
    sports_events = [
        {
            "name": "Annual Sports Day",
            "type": "Annual Event",
            "icon": "🏆",
            "desc": "Grand annual sports celebration with athletics, team games, and individual events. Held every year with prize distribution ceremony and cultural performances.",
            "highlights": ["Athletics (100m, 200m, 400m)", "Volleyball", "Basketball", "Cricket", "Tug of War", "Badminton"]
        },
        {
            "name": "Zonal Sports Competition",
            "type": "Inter-College",
            "icon": "🥇",
            "desc": "Inter-college zonal competition organized by UBTER. KLP students participate and represent the college at regional level in multiple sports disciplines.",
            "highlights": ["Inter-College Football", "Kabaddi", "Table Tennis", "Chess", "Athletics", "Hockey"]
        },
    ]

    return render_template(
        'home.html',
        departments=departments,
        hiring_partners=hiring_partners,
        sports_events=sports_events
    )


# ─── About Page (optional extra route) ───────────────────────────────────────

@main_bp.route('/about')
def about():
    """Render the about/college details page."""
    return render_template('home.html')  # Scroll to about section on homepage

================================================================================  END OF: routes/main.py  =====


################################################################################
#  FILE 6 of 18: routes/admin.py
#  TYPE: PYTHON
#  PURPOSE: Admin login, add/edit/delete students & subjects
################################################################################

"""
Admin panel routes for KLP Roorkee.
Protected by a simple ID/Password login.
Admins can add students, add subjects, and view/delete records.

Access credentials:
  ID       : KLP ROORKEE
  Password : Ubter@12345
"""

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session
)
from models import Student, Subject
from extensions import db

# Blueprint for admin routes — all URLs start with /admin
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ─── Hardcoded Admin Credentials ──────────────────────────────────────────────
ADMIN_ID       = "KLP ROORKEE"
ADMIN_PASSWORD = "Ubter@12345"


# ─── Login Required Decorator ─────────────────────────────────────────────────

def admin_required(f):
    """
    Decorator to protect admin routes.
    Redirects to login page if the admin is not logged in.
    """
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


# ─── Admin Login ──────────────────────────────────────────────────────────────

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET  → Show the admin login form.
    POST → Validate credentials and log in.
    """
    # If already logged in, go to dashboard
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        admin_id  = request.form.get('admin_id', '').strip()
        password  = request.form.get('password', '').strip()

        # Validate credentials (case-sensitive)
        if admin_id == ADMIN_ID and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Welcome! You are now logged in as Admin.', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid ID or Password. Please try again.', 'danger')

    return render_template('admin_login.html')


# ─── Admin Logout ─────────────────────────────────────────────────────────────

@admin_bp.route('/logout')
def logout():
    """Clear the admin session and redirect to login."""
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))


# ─── Admin Dashboard ──────────────────────────────────────────────────────────

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """
    Main admin dashboard.
    Shows a summary of all students in the database.
    """
    students = Student.query.order_by(Student.created_at.desc()).all()
    total_students = len(students)
    return render_template('admin_dashboard.html', students=students, total_students=total_students)


# ─── Add New Student ──────────────────────────────────────────────────────────

@admin_bp.route('/add-student', methods=['GET', 'POST'])
@admin_required
def add_student():
    """
    GET  → Show the add-student form.
    POST → Validate and save the new student to the database.
    """
    if request.method == 'POST':
        name          = request.form.get('name', '').strip()
        roll_number   = request.form.get('roll_number', '').strip()
        enrollment_no = request.form.get('enrollment_no', '').strip()
        father_name   = request.form.get('father_name', '').strip()
        category      = request.form.get('category', '').strip()
        branch        = request.form.get('branch', '').strip()
        institution   = request.form.get('institution', '').strip()
        semester      = request.form.get('semester', '').strip()
        academic_year = request.form.get('academic_year', '').strip()
        sgpa          = request.form.get('sgpa', '').strip()
        cgpa          = request.form.get('cgpa', '').strip()
        semester_result = request.form.get('semester_result', '').strip()

        # Basic validation
        errors = []
        if not all([name, roll_number, enrollment_no, father_name, category, branch, institution, semester, academic_year]):
            errors.append('All required fields must be filled.')
        if Student.query.filter_by(roll_number=roll_number).first():
            errors.append(f'Roll Number {roll_number} already exists.')
        if Student.query.filter_by(enrollment_no=enrollment_no).first():
            errors.append(f'Enrollment Number {enrollment_no} already exists.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('admin_add_student.html')

        # Create and save new student record
        student = Student(
            name=name,
            roll_number=roll_number,
            enrollment_no=enrollment_no,
            father_name=father_name,
            category=category,
            branch=branch,
            institution=institution,
            semester=int(semester),
            academic_year=academic_year,
            sgpa=float(sgpa) if sgpa else None,
            cgpa=float(cgpa) if cgpa else None,
            semester_result=semester_result or None
        )
        db.session.add(student)
        db.session.commit()

        flash(f'Student "{name}" added successfully! Now add their subjects.', 'success')
        return redirect(url_for('admin.add_subjects', student_id=student.id))

    return render_template('admin_add_student.html')


# ─── Add Subjects for a Student ───────────────────────────────────────────────

@admin_bp.route('/add-subjects/<int:student_id>', methods=['GET', 'POST'])
@admin_required
def add_subjects(student_id):
    """
    GET  → Show the add-subjects form for a student.
    POST → Save all submitted subjects (theory + practical, no limit).
    """
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        # Collect all subject entries submitted via the dynamic form
        # The form uses indexed field names: subject_code_0, subject_name_0, etc.
        subject_codes    = request.form.getlist('subject_code')
        subject_names    = request.form.getlist('subject_name')
        subject_types    = request.form.getlist('subject_type')
        max_marks_list   = request.form.getlist('max_marks')
        marks_obtained_list = request.form.getlist('marks_obtained')
        grades           = request.form.getlist('grade')
        results          = request.form.getlist('result')

        # Add each subject row to the database
        subjects_added = 0
        for i in range(len(subject_codes)):
            code = subject_codes[i].strip()
            name = subject_names[i].strip()
            if not code or not name:
                continue  # Skip empty rows

            subj = Subject(
                student_id=student.id,
                subject_code=code,
                subject_name=name,
                subject_type=subject_types[i] if i < len(subject_types) else 'Theory',
                max_marks=int(max_marks_list[i]) if i < len(max_marks_list) and max_marks_list[i] else 0,
                marks_obtained=int(marks_obtained_list[i]) if i < len(marks_obtained_list) and marks_obtained_list[i] else 0,
                grade=grades[i].strip() if i < len(grades) else None,
                result=results[i].strip() if i < len(results) else None,
            )
            db.session.add(subj)
            subjects_added += 1

        db.session.commit()
        flash(f'{subjects_added} subject(s) added for {student.name}.', 'success')
        return redirect(url_for('admin.view_student', student_id=student.id))

    # GET — show the form with existing subjects (for reference)
    existing_subjects = student.subjects
    return render_template('admin_add_subjects.html', student=student, existing_subjects=existing_subjects)


# ─── View Student Detail ──────────────────────────────────────────────────────

@admin_bp.route('/student/<int:student_id>')
@admin_required
def view_student(student_id):
    """Show full details of a student, including all their subjects."""
    student = Student.query.get_or_404(student_id)
    theory_subjects    = [s for s in student.subjects if s.subject_type == 'Theory']
    practical_subjects = [s for s in student.subjects if s.subject_type == 'Practical']
    return render_template(
        'admin_view_student.html',
        student=student,
        theory_subjects=theory_subjects,
        practical_subjects=practical_subjects
    )


# ─── Edit Student ─────────────────────────────────────────────────────────────

@admin_bp.route('/edit-student/<int:student_id>', methods=['GET', 'POST'])
@admin_required
def edit_student(student_id):
    """Edit a student's personal and academic details."""
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        student.name          = request.form.get('name', student.name).strip()
        student.roll_number   = request.form.get('roll_number', student.roll_number).strip()
        student.enrollment_no = request.form.get('enrollment_no', student.enrollment_no).strip()
        student.father_name   = request.form.get('father_name', student.father_name).strip()
        student.category      = request.form.get('category', student.category).strip()
        student.branch        = request.form.get('branch', student.branch).strip()
        student.institution   = request.form.get('institution', student.institution).strip()
        student.semester      = int(request.form.get('semester', student.semester))
        student.academic_year = request.form.get('academic_year', student.academic_year).strip()
        sgpa = request.form.get('sgpa', '').strip()
        cgpa = request.form.get('cgpa', '').strip()
        student.sgpa          = float(sgpa) if sgpa else None
        student.cgpa          = float(cgpa) if cgpa else None
        student.semester_result = request.form.get('semester_result', student.semester_result).strip()
        db.session.commit()
        flash('Student details updated successfully!', 'success')
        return redirect(url_for('admin.view_student', student_id=student.id))

    return render_template('admin_add_student.html', student=student, editing=True)


# ─── Delete Student ───────────────────────────────────────────────────────────

@admin_bp.route('/delete-student/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    """Delete a student and all their subjects (cascade delete)."""
    student = Student.query.get_or_404(student_id)
    name = student.name
    db.session.delete(student)
    db.session.commit()
    flash(f'Student "{name}" and all related data deleted.', 'warning')
    return redirect(url_for('admin.dashboard'))


# ─── Delete Single Subject ────────────────────────────────────────────────────

@admin_bp.route('/delete-subject/<int:subject_id>', methods=['POST'])
@admin_required
def delete_subject(subject_id):
    """Delete a single subject from a student's record."""
    subject = Subject.query.get_or_404(subject_id)
    student_id = subject.student_id
    db.session.delete(subject)
    db.session.commit()
    flash(f'Subject "{subject.subject_name}" deleted.', 'warning')
    return redirect(url_for('admin.view_student', student_id=student_id))

================================================================================  END OF: routes/admin.py  =====


################################################################################
#  FILE 7 of 18: routes/result.py
#  TYPE: PYTHON
#  PURPOSE: Student result search + ReportLab PDF generation
################################################################################

"""
Student Result routes.
Students can look up their result by entering a roll number or enrollment number.
Results display all subject marks, SGPA, CGPA, and can be downloaded as PDF.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from models import Student, Subject
import io

# Blueprint for result-related pages
result_bp = Blueprint('result', __name__, url_prefix='/result')


# ─── Result Lookup Page ───────────────────────────────────────────────────────

@result_bp.route('/', methods=['GET', 'POST'])
def result_home():
    """
    GET  → Show the roll number input form.
    POST → Look up the student and redirect to result display.
    """
    if request.method == 'POST':
        query = request.form.get('roll_number', '').strip()

        if not query:
            flash('Please enter your Roll Number or Enrollment Number.', 'warning')
            return redirect(url_for('result.result_home'))

        # Search by roll number OR enrollment number (case-insensitive)
        student = Student.query.filter(
            (Student.roll_number.ilike(query)) |
            (Student.enrollment_no.ilike(query))
        ).first()

        if student:
            # Redirect to the individual result page
            return redirect(url_for('result.show_result', student_id=student.id))
        else:
            flash(f'No result found for: {query}. Please check your Roll Number / Enrollment Number.', 'danger')
            return redirect(url_for('result.result_home'))

    # GET request — show the search form
    return render_template('result_search.html')


# ─── Display Individual Result ────────────────────────────────────────────────

@result_bp.route('/show/<int:student_id>')
def show_result(student_id):
    """
    Display the full marksheet for a student.
    Shows theory subjects, practical subjects, SGPA, CGPA, and semester result.
    """
    student = Student.query.get_or_404(student_id)

    # Separate theory and practical subjects for display
    theory_subjects    = [s for s in student.subjects if s.subject_type == 'Theory']
    practical_subjects = [s for s in student.subjects if s.subject_type == 'Practical']

    # Calculate totals
    theory_total_max      = sum(s.max_marks     for s in theory_subjects)
    theory_total_obtained = sum(s.marks_obtained for s in theory_subjects)
    practical_total_max      = sum(s.max_marks     for s in practical_subjects)
    practical_total_obtained = sum(s.marks_obtained for s in practical_subjects)
    grand_total_max      = theory_total_max      + practical_total_max
    grand_total_obtained = theory_total_obtained + practical_total_obtained

    return render_template(
        'result_display.html',
        student=student,
        theory_subjects=theory_subjects,
        practical_subjects=practical_subjects,
        theory_total_max=theory_total_max,
        theory_total_obtained=theory_total_obtained,
        practical_total_max=practical_total_max,
        practical_total_obtained=practical_total_obtained,
        grand_total_max=grand_total_max,
        grand_total_obtained=grand_total_obtained
    )


# ─── Download PDF Marksheet ───────────────────────────────────────────────────

@result_bp.route('/download/<int:student_id>')
def download_pdf(student_id):
    """
    Generate and download a PDF marksheet for the student.
    Uses ReportLab to create a formatted PDF in memory and serve it.
    """
    student = Student.query.get_or_404(student_id)

    theory_subjects    = [s for s in student.subjects if s.subject_type == 'Theory']
    practical_subjects = [s for s in student.subjects if s.subject_type == 'Practical']

    # Build the PDF in memory using ReportLab
    pdf_buffer = generate_marksheet_pdf(student, theory_subjects, practical_subjects)

    # Serve the PDF as a file download
    filename = f"Marksheet_{student.roll_number}_{student.name.replace(' ', '_')}.pdf"
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


# ─── PDF Generation Helper ────────────────────────────────────────────────────

def generate_marksheet_pdf(student, theory_subjects, practical_subjects):
    """
    Generate a professional PDF marksheet using ReportLab.
    Returns a BytesIO buffer containing the PDF data.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    buffer = io.BytesIO()

    # Create PDF document with A4 size and margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    story  = []  # List of flowable elements for the PDF

    # ── Custom styles ──────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Normal'],
        fontSize=16,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        textColor=colors.HexColor('#283593'),
        spaceAfter=2
    )
    small_center = ParagraphStyle(
        'SmallCenter',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#555555'),
        spaceAfter=2
    )
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold'
    )
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica'
    )

    # ── College Header ─────────────────────────────────────────────────────
    story.append(Paragraph("KANHAIYA LAL POLYTECHNIC ROORKEE (KLP)", title_style))
    story.append(Paragraph("Affiliated to Uttarakhand Board of Technical Education (UBTER), Roorkee", subtitle_style))
    story.append(Paragraph("Affiliated & Recognized by All India Council for Technical Education (AICTE)", small_center))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a237e')))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("SEMESTER MARKSHEET", ParagraphStyle(
        'SheetTitle',
        parent=styles['Normal'],
        fontSize=13,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        textColor=colors.HexColor('#c62828'),
        spaceAfter=6
    )))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1a237e')))
    story.append(Spacer(1, 0.3*cm))

    # ── Student Information Table ──────────────────────────────────────────
    info_data = [
        ["Student Name:", student.name,                  "Roll Number:", student.roll_number],
        ["Enrollment No:", student.enrollment_no,         "Father's Name:", student.father_name],
        ["Branch:", student.branch,                      "Category:", student.category],
        ["Institution:", student.institution,             "Semester:", f"Semester {student.semester}"],
        ["Academic Year:", student.academic_year,         "", ""],
    ]

    info_table = Table(info_data, colWidths=[3.5*cm, 5.5*cm, 3.5*cm, 5.5*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#1a237e')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f3f4f6'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.4*cm))

    # ── Theory Subjects Table ──────────────────────────────────────────────
    if theory_subjects:
        story.append(Paragraph("THEORY SUBJECTS", ParagraphStyle(
            'SectionHead',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            backColor=colors.HexColor('#1a237e'),
            leftIndent=4,
            spaceAfter=0
        )))

        th_header = [["S.No", "Subject Code", "Subject Name", "Max Marks", "Marks Obtained", "Grade", "Result"]]
        th_rows = []
        for i, s in enumerate(theory_subjects, 1):
            th_rows.append([
                str(i), s.subject_code, s.subject_name,
                str(s.max_marks), str(s.marks_obtained),
                s.grade or "-", s.result or "-"
            ])
        # Total row
        th_total_max = sum(s.max_marks for s in theory_subjects)
        th_total_obt = sum(s.marks_obtained for s in theory_subjects)
        th_rows.append(["", "TOTAL", "", str(th_total_max), str(th_total_obt), "", ""])

        th_data = th_header + th_rows
        th_table = Table(th_data, colWidths=[1*cm, 2.5*cm, 5.5*cm, 2*cm, 2.5*cm, 1.5*cm, 1.5*cm])
        th_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#e8eaf6')]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c5cae9')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#9fa8da')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(th_table)
        story.append(Spacer(1, 0.3*cm))

    # ── Practical Subjects Table ───────────────────────────────────────────
    if practical_subjects:
        story.append(Paragraph("PRACTICAL SUBJECTS", ParagraphStyle(
            'SectionHead2',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            backColor=colors.HexColor('#1b5e20'),
            leftIndent=4,
            spaceAfter=0
        )))

        pr_header = [["S.No", "Subject Code", "Subject Name", "Max Marks", "Marks Obtained", "Grade", "Result"]]
        pr_rows = []
        for i, s in enumerate(practical_subjects, 1):
            pr_rows.append([
                str(i), s.subject_code, s.subject_name,
                str(s.max_marks), str(s.marks_obtained),
                s.grade or "-", s.result or "-"
            ])
        pr_total_max = sum(s.max_marks for s in practical_subjects)
        pr_total_obt = sum(s.marks_obtained for s in practical_subjects)
        pr_rows.append(["", "TOTAL", "", str(pr_total_max), str(pr_total_obt), "", ""])

        pr_data = pr_header + pr_rows
        pr_table = Table(pr_data, colWidths=[1*cm, 2.5*cm, 5.5*cm, 2*cm, 2.5*cm, 1.5*cm, 1.5*cm])
        pr_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#e8f5e9')]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c8e6c9')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a5d6a7')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(pr_table)
        story.append(Spacer(1, 0.3*cm))

    # ── Result Summary Box ─────────────────────────────────────────────────
    grand_total_max = sum(s.max_marks for s in theory_subjects + practical_subjects)
    grand_total_obt = sum(s.marks_obtained for s in theory_subjects + practical_subjects)

    result_color = colors.HexColor('#1b5e20') if student.semester_result == 'PASS' else colors.HexColor('#b71c1c')

    summary_data = [
        ["Grand Total:", f"{grand_total_obt} / {grand_total_max}",
         "Percentage:", f"{(grand_total_obt/grand_total_max*100):.2f}%" if grand_total_max > 0 else "N/A"],
        ["SGPA:", str(student.sgpa or "N/A"),
         "CGPA:", str(student.cgpa or "N/A")],
        ["Semester Result:", student.semester_result or "N/A", "", ""],
    ]
    summary_table = Table(summary_data, colWidths=[3.5*cm, 4*cm, 3.5*cm, 7*cm])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#1a237e')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e3f2fd')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#90caf9')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('SPAN', (1, 2), (3, 2)),
        ('TEXTCOLOR', (1, 2), (1, 2), result_color),
        ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 2), (1, 2), 11),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.6*cm))

    # ── Footer / Signature Block ───────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1a237e')))
    story.append(Spacer(1, 0.2*cm))

    footer_data = [
        ["Student's Signature", "Examination Controller", "Principal"],
        ["___________________", "___________________", "___________________"],
        ["", "KLP Roorkee", "KLP Roorkee"],
    ]
    footer_table = Table(footer_data, colWidths=[6*cm, 6*cm, 6*cm])
    footer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(footer_table)
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "This is a computer-generated marksheet. Official seal required for verification. "
        "For queries, contact: info@klproorkee.edu.in | +91-1332-XXXXXX",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7,
                       alignment=TA_CENTER, textColor=colors.grey)
    ))

    # Build the PDF
    doc.build(story)
    buffer.seek(0)  # Rewind to beginning so Flask can read it
    return buffer
