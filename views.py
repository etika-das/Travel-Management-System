from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from travel.models import Package 
from travel.models import Booking, Destination, DistanceRange, Hotel, Transport
from datetime import datetime
from django.contrib.auth import logout

# HOME PAGE
def home(request):
    return render(request, 'travel/home.html')


# LOGIN VIEW (FIXED)
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')   
        else:
            return render(request, 'travel/login.html', {'error': 'Invalid credentials'})

    return render(request, 'travel/login.html')

# SIGNUP (simple page for now)
def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'travel/signup.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, password=password)
        user.save()

        # AUTO LOGIN
        login(request, user)

        return redirect('dashboard')
    return render(request, 'travel/signup.html')
    
def user_logout(request):
        logout(request)
        return redirect ('login')

    
# DASHBOARD (after login)
@login_required
def dashboard(request):
    bookings= Booking.objects.filter(user=request.user)
    return render(request, 'travel/dashboard.html', {'bookings' : bookings })


# BOOK TRIP PAGE

@login_required
def package_list(request):
    packages = Package.objects.all()   # get all data
    return render(request, 'travel/package_list.html', {'packages': packages})

@login_required
def custom_trip(request):
    data = Package.objects.all()   # fetch all your DB data
    return render(request, 'travel/custom_trip.html', {'data': data})

@login_required
def book_package(request, package_id):
    package = get_object_or_404(Package, id=package_id)

    if request.method == "POST":
        people = int(request.POST.get('people'))
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')

        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")

        days = (end_date - start_date).days

        total_price = package.price_per_person * people
        final_price = total_price  # you can add discount later

        booking=Booking.objects.create(
            user=request.user,
            booking_type="package",
            package=package,
            destination=package.destination,
            hotel=package.hotel,
            transport=package.transport,
            starting_date=start_date,
            ending_date=end_date,
            no_of_people=people,
            no_of_days=days,
            no_of_rooms=1,
            total_price=total_price,
            final_price=final_price
        
        )

        return redirect('payment_page', booking_id = booking.id)
    return render(request, 'travel/book_package.html', {'package': package})

@login_required
def custom_trip_step1(request):
    destinations = Destination.objects.all()
    return render(request, "travel/custom/step1.html", {"destinations": destinations})

def custom_trip_step2(request, destination_id):

    request.session['destination_id'] = destination_id

    hotels = Hotel.objects.filter(destination_id=destination_id)

    return render(request, "travel/custom/step2.html", {
        "hotels": hotels
    })

def custom_trip_step3(request, hotel_id):

    request.session['hotel_id'] = hotel_id

    hotel = Hotel.objects.get(id=hotel_id)

    return render(request, "travel/custom/step3.html", {
        "hotel": hotel
    })  
@login_required
def custom_trip_step4(request):

    transports = Transport.objects.all()
    distances = DistanceRange.objects.all()

    if request.method == "POST":
        request.session['rooms'] = request.POST.get('rooms')
        request.session['people'] = request.POST.get('people')
        request.session['start_date'] = request.POST.get('start_date')
        request.session['end_date'] = request.POST.get('end_date')

    return render(request, "travel/custom/step4.html", {
        "transports": transports,
        "distances": distances
    })

    # if someone opens directly
    return redirect('custom_trip_step1')
    
from datetime import datetime

@login_required
def custom_trip_confirm(request):

    if request.method != "POST":
        return redirect('custom_trip_step1')

    destination = Destination.objects.get(id=request.session.get('destination_id'))
    hotel = Hotel.objects.get(id=request.session.get('hotel_id'))
    transport = Transport.objects.get(id=request.POST.get('transport'))
    distance = DistanceRange.objects.get(id=request.POST.get('distance'))

    rooms = int(request.session.get('rooms'))
    people = int(request.session.get('people'))

    start_date = datetime.strptime(request.session.get('start_date'), "%Y-%m-%d")
    end_date = datetime.strptime(request.session.get('end_date'), "%Y-%m-%d")

    days = (end_date - start_date).days
    if days <= 0:
        days = 1

    # 💰 PRICE CALCULATION
    hotel_cost = hotel.price_per_night * rooms * days

    # optional: transport per person logic
    transport_cost = distance.price_per_person * people

    total_price = hotel_cost + transport_cost

    booking = Booking.objects.create(
        user=request.user,
        booking_type="custom",
        destination=destination,
        hotel=hotel,
        transport=transport,
        distance_range=distance,
        starting_date=start_date,
        ending_date=end_date,
        no_of_rooms=rooms,
        no_of_people=people,
        no_of_days=days,
        total_price=total_price,
        final_price=total_price
    )

    return redirect("payment_page", booking_id=booking.id)
def payment_page(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    

    return render(request, "travel/payment.html", {
        "booking": booking,
        "total_price": booking.final_price
    })
    
@login_required
def booking_dashboard(request):
    bookings = Booking.objects.filter(user=request.user)

    return render(request,
        'travel/booking_dashboard.html',
        {'bookings': bookings}
    )    
