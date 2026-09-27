from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.common.constants import EmploymentType, JobStatus
from apps.jobs.models import Job


class JobFilter(django_filters.FilterSet):
    location = django_filters.CharFilter(lookup_expr="icontains")
    department = django_filters.CharFilter(method="filter_department")
    degree = django_filters.CharFilter(method="filter_degree")
    employment_type = django_filters.ChoiceFilter(choices=EmploymentType.choices)
    status = django_filters.ChoiceFilter(choices=JobStatus.choices)
    salary_min = django_filters.NumberFilter(field_name="salary_min", lookup_expr="gte")
    salary_max = django_filters.NumberFilter(field_name="salary_max", lookup_expr="lte")
    graduation_year = django_filters.NumberFilter(field_name="graduation_year")

    class Meta:
        model = Job
        fields = [
            "location",
            "department",
            "degree",
            "employment_type",
            "status",
            "salary_min",
            "salary_max",
            "graduation_year",
        ]

    def filter_department(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(eligible_departments=[])
            | Q(eligible_departments__contains=value)
            | Q(eligible_departments__contains=[value])
        )

    def filter_degree(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(eligible_degrees=[])
            | Q(eligible_degrees__contains=value)
            | Q(eligible_degrees__contains=[value])
        )
