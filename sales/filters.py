import django_filters
from .models import Ad
from django.utils.dateparse import parse_date
from django.db.models import Q

class AdFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method="filter_search",
        label="Search"
    )
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.NumberFilter(field_name="category_id")
    location = django_filters.CharFilter(field_name="location", lookup_expr="icontains")
    event_date = django_filters.DateFilter(field_name="event_date")

    class Meta:
        model = Ad
        fields = ["q", "category", "location", "min_price", "max_price", "event_date"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value)
        )
