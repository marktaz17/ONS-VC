def home(request):
    records = building_record.objects.all()
    if request.user.is_authenticated:

        return render(request, 'home.html',{'records':records})
    else:
        messages.warning(request, "You must be Logged In to view the page!")
        return redirect('login_page')