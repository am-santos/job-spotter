from django.shortcuts import render
from core.models import Company, Job

def home(request):
    companies = Company.objects.all()
    jobs = Job.objects.all()
    return render(request, 'dashboard/home.html', {'companies': companies, 'jobs': jobs})
