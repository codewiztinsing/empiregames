from django.shortcuts import render
import csv
from django.http import HttpResponse
from users.models import User
# give me the view  to export play data to csv
def export_play_data_to_csv(request):
    if request.method == 'POST':
        users = User.objects.all()
       
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users_data.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow([
            'ID',
            'Username', 
            'Email',
            'First Name',
            'Last Name',
            'Phone',
            'Telegram ID',
            'Referral Code',
            'Date Joined',
            'Last Login',
            'Is Active',
            'Is Staff',
            'Is Superuser'
        ])
        
        # Write user data rows
        for user in users:
            writer.writerow([
                user.id,
                user.username,
                user.email,
                user.first_name,
                user.last_name,
                user.phone,
                user.telegram_id,
                user.referral_code,
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else '',
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '',
                user.is_active,
                user.is_staff,
                user.is_superuser
            ])
        
        return response
    
    return render(request, 'marketing/export_play_data_to_csv.html')