
"""
Database models for the KLP Student Result System.
Defines Student and Subject tables using SQLAlchemy ORM.
"""

from extensions import db
from datetime import datetime


# ─── Student Model ────────────────────────────────────────────────────────────

class Student(db.Model):
    """
    Stores personal and academic details for each student.
    One student can have multiple subjects (one-to-many relationship).
    """
    __tablename__ = 'students'

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(150), nullable=False)            # Student full name
    roll_number     = db.Column(db.String(50), unique=True, nullable=False) # Exam roll number
    enrollment_no   = db.Column(db.String(50), unique=True, nullable=False) # College enrollment number
    father_name     = db.Column(db.String(150), nullable=False)            # Father's full name
    category        = db.Column(db.String(20), nullable=False)             # GEN / OBC / SC / ST / EWS
    branch          = db.Column(db.String(100), nullable=False)            # Department/Branch name
    institution     = db.Column(db.String(200), nullable=False)            # Institution name
    semester        = db.Column(db.Integer, nullable=False)                # Current semester (1-6)
    academic_year   = db.Column(db.String(20), nullable=False)             # e.g. "2023-2024"
    sgpa            = db.Column(db.Float, nullable=True)                   # Semester Grade Point Average
    cgpa            = db.Column(db.Float, nullable=True)                   # Cumulative Grade Point Average
    semester_result = db.Column(db.String(20), nullable=True)             # PASS / FAIL / BACKLOG
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)     # Record creation timestamp

    # Relationship: one student → many subjects
    subjects = db.relationship('Subject', backref='student', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Student {self.name} | Roll: {self.roll_number}>'


# ─── Subject Model ────────────────────────────────────────────────────────────

class Subject(db.Model):
    """
    Stores individual subject marks for a student.
    Each row is one subject (theory or practical) linked to a student.
    """
    __tablename__ = 'subjects'

    id              = db.Column(db.Integer, primary_key=True)
    student_id      = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)  # Link to student

    subject_code    = db.Column(db.String(20), nullable=False)    # Subject code (e.g. ME-101)
    subject_name    = db.Column(db.String(200), nullable=False)   # Full subject name
    subject_type    = db.Column(db.String(20), nullable=False)    # "Theory" or "Practical"
    max_marks       = db.Column(db.Integer, nullable=False)        # Maximum marks for the subject
    marks_obtained  = db.Column(db.Integer, nullable=False)        # Marks scored by student
    grade           = db.Column(db.String(5), nullable=True)       # Letter grade (A, B+, etc.)
    result          = db.Column(db.String(10), nullable=True)      # PASS / FAIL for this subject

    def __repr__(self):
        return f'<Subject {self.subject_name} | Marks: {self.marks_obtained}/{self.max_marks}>'
