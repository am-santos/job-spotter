
import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_spotter.settings')
django.setup()

from core.models import Company, Job, UserProfile
from django.contrib.auth.models import User

def verify():
    # Clean up
    User.objects.all().delete()
    Company.objects.all().delete()

    # Create dummy data
    user = User.objects.create_user(username='testuser', password='password')
    UserProfile.objects.create(user=user, text_resume='My Resume')

    company = Company.objects.create(name='TechCorp', url='http://techcorp.com')
    Job.objects.create(company=company, title='Developer', description='Write code', match_score=95.0)

    # Check persistence
    assert Company.objects.count() == 1
    assert Job.objects.count() == 1
    print("Models verified.")

    # Check dashboard
    c = Client()
    response = c.get('/')
    assert response.status_code == 200
    assert 'TechCorp' in response.content.decode()
    assert 'Developer' in response.content.decode()
    print("Dashboard verified.")

if __name__ == '__main__':
    verify()
