from django.shortcuts import render

def wshome(request):
    return render(request, 'wshome.html')