from django.db import models



class AdminUser(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username



class Destination(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Hotel(models.Model):
    name = models.CharField(max_length=100)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    price_per_night = models.FloatField()

    def __str__(self):
        return self.name



class Transport(models.Model):
    transport_type = models.CharField(max_length=50)

    def __str__(self):
        return self.transport_type


class DistanceRange(models.Model):
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE)
    min_distance = models.IntegerField()
    max_distance = models.IntegerField()
    price_per_person = models.FloatField()

    def __str__(self):
        return f"{self.min_distance}-{self.max_distance}"



class Package(models.Model):
    name = models.CharField(max_length=200)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE)
    duration = models.IntegerField()
    price_per_person = models.FloatField()

    def __str__(self):
        return self.name



class Booking(models.Model):
    from django.contrib.auth.models import User
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    booking_type = models.CharField(
        max_length=20,
        choices=[
            ('package', 'Package Booking'),
            ('custom', 'Custom Trip')
        ],
        null=True,
        blank=True
    )

    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, blank=True)
    transport = models.ForeignKey(Transport, on_delete=models.SET_NULL, null=True, blank=True)
    distance_range = models.ForeignKey(DistanceRange, on_delete=models.SET_NULL, null=True, blank=True)

    starting_date = models.DateField(null=True, blank=True)
    ending_date = models.DateField(null=True, blank=True)

    no_of_people = models.IntegerField(default=1)
    no_of_days = models.IntegerField(default=1)
    no_of_rooms = models.IntegerField(default=1)

    total_price = models.FloatField()
    final_price = models.FloatField()

    def __str__(self):
        return f"{self.booking_type} - {self.user.username}"

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    payment_status = models.CharField(max_length=50)

    def __str__(self):
        return f"Payment {self.id}"