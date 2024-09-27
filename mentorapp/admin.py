from django.contrib import admin
from .models import Mentor
from .models import Coordinate
from .models import Style

admin.site.register(Mentor)
admin.site.register(Coordinate)
admin.site.register(Style)