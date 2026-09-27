"""Populate a realistic demo campus so the UI is immediately usable."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.applications.models import Application, ApplicationStatusHistory
from apps.applications.services import apply_to_job, change_application_status
from apps.common.constants import (
    ApplicationStatus,
    CompanyVerificationStatus,
    Degree,
    Department,
    EmploymentType,
    JobStatus,
    Role,
)
from apps.companies.models import Company
from apps.interviews.models import Interview
from apps.jobs.models import Job
from apps.notifications.models import Notification
from apps.recruiters.models import RecruiterProfile
from apps.students.models import Education, Skill, StudentProfile, StudentSkill

User = get_user_model()

DEMO_PASSWORD = "CampusHire@123"

MINIMAL_PDF = b"""%PDF-1.1
1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj
2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj
3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] >>endobj
xref
0 4
trailer<< /Root 1 0 R /Size 4 >>
startxref
0
%%EOF
"""


class Command(BaseCommand):
    help = "Seed demo users, companies, jobs, applications, interviews, and notifications."

    @transaction.atomic
    def handle(self, *args, **options):
        skills = self._skills()
        self._user("admin@campushire.local", "Asha", "Menon", Role.ADMIN, staff=True)
        students = self._students(skills)
        _recruiters, companies = self._recruiters()
        jobs = self._jobs(companies, skills)
        self._applications(students, jobs)
        self.stdout.write(self.style.SUCCESS("Seed data ready."))
        self.stdout.write("  Admin     admin@campushire.local        / CampusHire@123")
        self.stdout.write("  Student   priya.sharma@campushire.local / CampusHire@123")
        self.stdout.write("  Recruiter rec.nimbus@campushire.local   / CampusHire@123")

    def _user(self, email, first, last, role, staff=False):
        user, _created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first,
                "last_name": last,
                "role": role,
                "is_staff": staff or role == Role.ADMIN,
                "is_superuser": role == Role.ADMIN,
            },
        )
        user.set_password(DEMO_PASSWORD)
        user.first_name = first
        user.last_name = last
        user.role = role
        user.is_staff = staff or role == Role.ADMIN
        user.is_superuser = role == Role.ADMIN
        user.is_active = True
        user.save()
        return user

    def _skills(self):
        mapping = {}
        for name in [
            "Python",
            "Django",
            "Java",
            "SQL",
            "JavaScript",
            "React",
            "Data Structures",
            "Machine Learning",
            "Communication",
            "Excel",
        ]:
            mapping[name], _ = Skill.objects.get_or_create(name=name)
        return mapping

    def _students(self, skills):
        specs = [
            {
                "email": "priya.sharma@campushire.local",
                "first": "Priya",
                "last": "Sharma",
                "reg": "CSE2022001",
                "dept": Department.CSE,
                "degree": Degree.BTECH,
                "year": 2026,
                "cgpa": Decimal("8.70"),
                "backlogs": 0,
                "skills": ["Python", "Django", "SQL", "JavaScript", "Data Structures"],
            },
            {
                "email": "arjun.nair@campushire.local",
                "first": "Arjun",
                "last": "Nair",
                "reg": "ECE2022014",
                "dept": Department.ECE,
                "degree": Degree.BTECH,
                "year": 2026,
                "cgpa": Decimal("7.20"),
                "backlogs": 1,
                "skills": ["Java", "SQL", "Communication"],
            },
            {
                "email": "meera.iyer@campushire.local",
                "first": "Meera",
                "last": "Iyer",
                "reg": "IT2021092",
                "dept": Department.IT,
                "degree": Degree.BTECH,
                "year": 2025,
                "cgpa": Decimal("9.10"),
                "backlogs": 0,
                "skills": ["Python", "Machine Learning", "SQL", "JavaScript"],
            },
            {
                "email": "rahul.verma@campushire.local",
                "first": "Rahul",
                "last": "Verma",
                "reg": "MECH2021188",
                "dept": Department.MECH,
                "degree": Degree.BE,
                "year": 2025,
                "cgpa": Decimal("6.40"),
                "backlogs": 3,
                "skills": ["Excel", "Communication"],
            },
            {
                "email": "nisha.patel@campushire.local",
                "first": "Nisha",
                "last": "Patel",
                "reg": "MBA2024011",
                "dept": Department.MBA,
                "degree": Degree.MBA,
                "year": 2026,
                "cgpa": Decimal("8.10"),
                "backlogs": 0,
                "skills": ["Excel", "Communication"],
            },
        ]
        profiles = []
        for spec in specs:
            user = self._user(spec["email"], spec["first"], spec["last"], Role.STUDENT)
            profile, _ = StudentProfile.objects.update_or_create(
                user=user,
                defaults={
                    "registration_number": spec["reg"],
                    "phone": "9876500000",
                    "department": spec["dept"],
                    "degree": spec["degree"],
                    "graduation_year": spec["year"],
                    "cgpa": spec["cgpa"],
                    "backlogs": spec["backlogs"],
                    "github_url": "https://github.com/example",
                    "linkedin_url": "https://linkedin.com/in/example",
                },
            )
            if not profile.resume:
                profile.resume.save(f"{spec['reg']}.pdf", ContentFile(MINIMAL_PDF), save=True)
            Education.objects.get_or_create(
                student=profile,
                institution="National Institute of Technology",
                degree=spec["degree"],
                defaults={
                    "field_of_study": spec["dept"],
                    "start_year": spec["year"] - 4,
                    "end_year": spec["year"],
                    "score": str(spec["cgpa"]),
                },
            )
            profile.student_skills.all().delete()
            for name in spec["skills"]:
                StudentSkill.objects.create(student=profile, skill=skills[name], proficiency="ADVANCED")
            profiles.append(profile)
        return profiles

    def _recruiters(self):
        data = [
            {
                "email": "rec.nimbus@campushire.local",
                "first": "Kavya",
                "last": "Rao",
                "designation": "Campus Lead",
                "company": "Nimbus Labs",
                "industry": "Software",
                "location": "Bengaluru",
                "website": "https://nimbuslabs.example",
                "status": CompanyVerificationStatus.VERIFIED,
                "description": "Product engineering studio building developer tools.",
            },
            {
                "email": "rec.helix@campushire.local",
                "first": "Vikram",
                "last": "Shah",
                "designation": "Talent Partner",
                "company": "Helix Finance",
                "industry": "FinTech",
                "location": "Mumbai",
                "website": "https://helixfinance.example",
                "status": CompanyVerificationStatus.VERIFIED,
                "description": "Consumer finance and payments platform.",
            },
            {
                "email": "rec.northpeak@campushire.local",
                "first": "Ananya",
                "last": "Das",
                "designation": "HR Manager",
                "company": "Northpeak Systems",
                "industry": "Consulting",
                "location": "Hyderabad",
                "website": "https://northpeak.example",
                "status": CompanyVerificationStatus.PENDING,
                "description": "IT consulting and enterprise transformation.",
            },
        ]
        recruiters = []
        companies = []
        for row in data:
            user = self._user(row["email"], row["first"], row["last"], Role.RECRUITER)
            RecruiterProfile.objects.update_or_create(
                user=user, defaults={"designation": row["designation"], "phone": "9800011111"}
            )
            company, _ = Company.objects.update_or_create(
                company_name=row["company"],
                defaults={
                    "owner": user,
                    "description": row["description"],
                    "website": row["website"],
                    "industry": row["industry"],
                    "location": row["location"],
                    "verification_status": row["status"],
                },
            )
            recruiters.append(user)
            companies.append(company)
        return recruiters, companies

    def _jobs(self, companies, skills):
        nimbus, helix, _northpeak = companies
        now = timezone.now()
        specs = [
            {
                "company": nimbus,
                "title": "Backend Engineer Intern",
                "description": "Build REST APIs with Django, write tests, and ship campus-scale features.",
                "employment_type": EmploymentType.INTERNSHIP,
                "location": "Bengaluru",
                "minimum_cgpa": Decimal("7.00"),
                "maximum_backlogs": 1,
                "eligible_departments": [Department.CSE, Department.IT],
                "eligible_degrees": [Degree.BTECH, Degree.BE],
                "graduation_year": 2026,
                "salary_min": 25000,
                "salary_max": 40000,
                "skills": ["Python", "Django", "SQL"],
                "status": JobStatus.ACTIVE,
                "application_deadline": now + timedelta(days=21),
            },
            {
                "company": nimbus,
                "title": "Full Stack Graduate Hire",
                "description": "Own features across Django APIs and a template-driven frontend.",
                "employment_type": EmploymentType.FULL_TIME,
                "location": "Bengaluru",
                "minimum_cgpa": Decimal("8.00"),
                "maximum_backlogs": 0,
                "eligible_departments": [Department.CSE, Department.IT],
                "eligible_degrees": [Degree.BTECH],
                "graduation_year": 2026,
                "salary_min": 800000,
                "salary_max": 1200000,
                "skills": ["Python", "Django", "JavaScript"],
                "status": JobStatus.ACTIVE,
                "application_deadline": now + timedelta(days=14),
            },
            {
                "company": helix,
                "title": "Data Analyst",
                "description": "SQL-heavy analytics on payment and credit datasets.",
                "employment_type": EmploymentType.FULL_TIME,
                "location": "Mumbai",
                "minimum_cgpa": Decimal("7.50"),
                "maximum_backlogs": 0,
                "eligible_departments": [Department.CSE, Department.IT, Department.ECE],
                "eligible_degrees": [Degree.BTECH, Degree.BE],
                "graduation_year": 2025,
                "salary_min": 700000,
                "salary_max": 900000,
                "skills": ["SQL", "Python"],
                "status": JobStatus.ACTIVE,
                "application_deadline": now + timedelta(days=10),
            },
            {
                "company": helix,
                "title": "Campus MBA Associate",
                "description": "Rotate across product, operations, and credit policy.",
                "employment_type": EmploymentType.FULL_TIME,
                "location": "Mumbai",
                "minimum_cgpa": Decimal("7.00"),
                "maximum_backlogs": 0,
                "eligible_departments": [Department.MBA],
                "eligible_degrees": [Degree.MBA],
                "graduation_year": 2026,
                "salary_min": 900000,
                "salary_max": 1100000,
                "skills": ["Excel", "Communication"],
                "status": JobStatus.ACTIVE,
                "application_deadline": now + timedelta(days=30),
            },
            {
                "company": nimbus,
                "title": "Expired QA Intern",
                "description": "This role is closed because the deadline passed.",
                "employment_type": EmploymentType.INTERNSHIP,
                "location": "Chennai",
                "minimum_cgpa": Decimal("6.00"),
                "maximum_backlogs": 2,
                "eligible_departments": [],
                "eligible_degrees": [],
                "graduation_year": None,
                "salary_min": 15000,
                "salary_max": 20000,
                "skills": [],
                "status": JobStatus.CLOSED,
                "application_deadline": now - timedelta(days=3),
            },
            {
                "company": helix,
                "title": "Pending Platform Engineer",
                "description": "Awaiting placement cell approval.",
                "employment_type": EmploymentType.FULL_TIME,
                "location": "Pune",
                "minimum_cgpa": Decimal("8.50"),
                "maximum_backlogs": 0,
                "eligible_departments": [Department.CSE],
                "eligible_degrees": [Degree.BTECH],
                "graduation_year": 2026,
                "salary_min": 1000000,
                "salary_max": 1400000,
                "skills": ["Python", "Django"],
                "status": JobStatus.PENDING_APPROVAL,
                "application_deadline": now + timedelta(days=40),
            },
        ]
        jobs = []
        for spec in specs:
            skill_names = spec.pop("skills")
            job, _ = Job.objects.update_or_create(
                company=spec["company"],
                title=spec["title"],
                defaults=spec,
            )
            job.required_skills.set([skills[n] for n in skill_names])
            jobs.append(job)
        return jobs

    def _ensure_application(self, student, job):
        existing = Application.objects.filter(student=student, job=job).first()
        if existing:
            return existing
        try:
            return apply_to_job(student=student, job=job, cover_letter="I am excited to contribute.")
        except Exception:
            application = Application.objects.create(
                student=student, job=job, cover_letter="I am excited to contribute."
            )
            ApplicationStatusHistory.objects.create(
                application=application,
                old_status="",
                new_status=ApplicationStatus.APPLIED,
                changed_by=student.user,
            )
            return application

    def _advance(self, application, target, actor):
        order = [
            ApplicationStatus.UNDER_REVIEW,
            ApplicationStatus.SHORTLISTED,
            ApplicationStatus.INTERVIEW_SCHEDULED,
            ApplicationStatus.SELECTED,
        ]
        if target not in order and target != ApplicationStatus.UNDER_REVIEW:
            chain = []
            if target == ApplicationStatus.SHORTLISTED:
                chain = [ApplicationStatus.UNDER_REVIEW, ApplicationStatus.SHORTLISTED]
            elif target == ApplicationStatus.SELECTED:
                chain = [ApplicationStatus.UNDER_REVIEW, ApplicationStatus.SHORTLISTED, ApplicationStatus.SELECTED]
            elif target == ApplicationStatus.UNDER_REVIEW:
                chain = [ApplicationStatus.UNDER_REVIEW]
        else:
            chain = []
            for status in [ApplicationStatus.UNDER_REVIEW, ApplicationStatus.SHORTLISTED, ApplicationStatus.SELECTED]:
                chain.append(status)
                if status == target:
                    break
        application.refresh_from_db()
        for status in chain:
            if application.status == status:
                continue
            try:
                change_application_status(application=application, new_status=status, actor=actor, remarks="Seed")
                application.refresh_from_db()
            except ValueError:
                break

    def _applications(self, students, jobs):
        priya, _arjun, meera, _rahul, nisha = students
        intern, fullstack, analyst, mba_role, _expired, _pending = jobs
        mapping = [
            (priya, intern, ApplicationStatus.SHORTLISTED),
            (priya, fullstack, ApplicationStatus.APPLIED),
            (meera, analyst, ApplicationStatus.SELECTED),
            (nisha, mba_role, ApplicationStatus.UNDER_REVIEW),
        ]
        for student, job, target in mapping:
            application = self._ensure_application(student, job)
            if application.status != target:
                self._advance(application, target, job.company.owner)

        priya_intern = Application.objects.filter(student=priya, job=intern).first()
        if priya_intern and not Interview.objects.filter(application=priya_intern).exists():
            from apps.interviews.services import schedule_interview

            priya_intern.refresh_from_db()
            try:
                schedule_interview(
                    application=priya_intern,
                    scheduled_at=timezone.now() + timedelta(days=5),
                    mode="ONLINE",
                    interviewer_name="Kavya Rao",
                    meeting_link="https://meet.example.com/nimbus-priya",
                    actor=intern.company.owner,
                )
            except Exception:
                Interview.objects.create(
                    application=priya_intern,
                    scheduled_at=timezone.now() + timedelta(days=5),
                    mode="ONLINE",
                    interviewer_name="Kavya Rao",
                    meeting_link="https://meet.example.com/nimbus-priya",
                )
        Notification.objects.get_or_create(
            recipient=User.objects.get(email="admin@campushire.local"),
            title="Placement season is live",
            defaults={
                "message": "Review pending companies and job postings.",
                "notification_type": "SYSTEM",
            },
        )
