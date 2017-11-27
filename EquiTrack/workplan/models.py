from django.db import models


class Workplan(models.Model):
    """
    Represents a work plan for the country programme

    Relates to :model:`reports.CountryProgramme`
    """

    STATUS = (
        ("On Track", "On Track"),
        ("Constrained", "Constrained"),
        ("No Progress", "No Progress"),
        ("Target Met", "Target Met"),
    )
    status = models.CharField(max_length=32, null=True, blank=True, choices=STATUS)
    country_programme = models.ForeignKey('reports.CountryProgramme')
