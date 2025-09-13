from django.shortcuts import render, redirect
from .models import Banner
from .forms import BannerForm

def upload_banner(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            banner = form.save(commit=False)
            if 'image' in request.FILES:
                banner.image = request.FILES['image']
            banner.save()
            return redirect('dashboard:dashboard')
    else:
        form = BannerForm()

    return render(request, 'dashboard/index.html')