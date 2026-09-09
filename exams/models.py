from decimal import Decimal
from django.db import models
from django.urls import reverse


def calculate_grade(percentage):
    """
    Standard Pakistani / KP Board School Grading System.
    """
    if percentage is None:
        return "-"
    pct = float(percentage)
    if pct >= 80.0:
        return "A+"
    elif pct >= 70.0:
        return "A"
    elif pct >= 60.0:
        return "B"
    elif pct >= 50.0:
        return "C"
    elif pct >= 40.0:
        return "D"
    elif pct >= 33.0:
        return "E"
    else:
        return "Fail"


def get_position_suffix(position):
    """
    Converts 1 -> 1st, 2 -> 2nd, 3 -> 3rd, etc.
    """
    if not position:
        return "-"
    pos = int(position)
    if 10 <= pos % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(pos % 10, "th")
    return f"{pos}{suffix}"


class Exam(models.Model):
    """
    Represents an Examination term (e.g. First Term Examination 2026, Annual Examination 2026).
    """
    name = models.CharField(max_length=150, help_text="e.g. First Term Examination 2026")
    session = models.ForeignKey(
        "school.AcademicSession",
        on_delete=models.CASCADE,
        related_name="exams",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_active", "-created_at"]
        verbose_name = "Examination"
        verbose_name_plural = "Examinations"

    def __str__(self):
        return f"{self.name} ({self.session.name if self.session else ''})"


class Subject(models.Model):
    """
    Master list of subjects taught across all grades.
    """
    name = models.CharField(max_length=100, unique=True, help_text="e.g. English, Mathematics, Biology")
    code = models.CharField(max_length=20, blank=True, help_text="Short name for result header e.g. Eng, Maths, Bio, M.quran")
    order = models.IntegerField(default=0, help_text="Display sequence order")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def __str__(self):
        return self.name

    @property
    def short_name(self):
        return self.code if self.code else self.name


class ClassSubject(models.Model):
    """
    Maps which subjects belong to which class, with default maximum & passing marks.
    Allows flexibly increasing or decreasing subjects per class.
    """
    class_level = models.ForeignKey(
        "school.ClassLevel",
        on_delete=models.CASCADE,
        related_name="class_subjects",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="class_subjects",
    )
    total_marks = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=100.0,
        help_text="Maximum marks for this paper in this class (e.g. 75, 50, 100)",
    )
    passing_marks = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=33.0,
        help_text="Passing threshold marks (e.g. 25, 17, 33)",
    )
    order = models.IntegerField(default=0, help_text="Column display order in result sheet")

    class Meta:
        unique_together = ("class_level", "subject")
        ordering = ["order", "subject__order", "subject__name"]
        verbose_name = "Class Subject"
        verbose_name_plural = "Class Subjects"

    def __str__(self):
        return f"{self.class_level.name} - {self.subject.short_name} ({int(self.total_marks) if self.total_marks % 1 == 0 else self.total_marks})"

    @property
    def header_label(self):
        """Returns header formatted as seen in official result sheets: e.g. Eng (75)"""
        m = int(self.total_marks) if self.total_marks % 1 == 0 else self.total_marks
        return f"{self.subject.short_name} ({m})"


class ExamMark(models.Model):
    """
    Stores obtained marks for a student in a specific subject of an examination.
    """
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="marks",
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="exam_marks",
    )
    class_level = models.ForeignKey(
        "school.ClassLevel",
        on_delete=models.CASCADE,
        related_name="exam_marks",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="exam_marks",
    )
    total_marks = models.DecimalField(max_digits=5, decimal_places=1, default=100.0)
    obtained_marks = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)
    is_absent = models.BooleanField(default=False)
    remarks = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("exam", "student", "subject")
        ordering = ["student__admission_no", "subject__order"]
        verbose_name = "Exam Mark"
        verbose_name_plural = "Exam Marks"

    def __str__(self):
        if self.is_absent:
            return f"{self.student.full_name} - {self.subject.short_name}: Absent"
        return f"{self.student.full_name} - {self.subject.short_name}: {self.obtained_marks}/{self.total_marks}"

    @property
    def percentage(self):
        if self.is_absent or self.total_marks <= 0:
            return 0.0
        return round((float(self.obtained_marks) / float(self.total_marks)) * 100, 1)

    @property
    def display_score(self):
        if self.is_absent:
            return "A"
        return int(self.obtained_marks) if self.obtained_marks % 1 == 0 else self.obtained_marks
