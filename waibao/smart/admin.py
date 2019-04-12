from django.contrib import admin
from .import models
#from django.db import models
# Register your models here.

from smart.models import User
from smart.models import Total
from smart.models import Record
from smart.models import Part
from smart.models import Person
from smart.models import  Buzzword
from smart.models import  Count
admin.site.register(User)
admin.site.register(Total)
admin.site.register(Record)
admin.site.register(Part)
admin.site.register(Person)
admin.site.register(Buzzword)
admin.site.register(Count)
