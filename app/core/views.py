from django.shortcuts import render

def custom_404(request, exception):
    print("404 error")
    return render(request, '404.html', status=404)


def custom_500(request):
    print("500 error")
    return render(request, '500.html', status=500)