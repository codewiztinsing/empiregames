from django.contrib import admin
from .models import Agent

# Register your models here.

class AgentAdmin(admin.ModelAdmin):
    list_display = ("id",'name', 'phone', 'agent_code')
    search_fields = ('name', 'phone', 'agent_code')
    list_per_page = 10

admin.site.register(Agent, AgentAdmin)