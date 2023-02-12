import calendar
import datetime

import pandas as pd
import requests
from dateutil import parser
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from psycopg2 import DatabaseError

from .forms import CustomerForm, UserForm, LoginUserForm, ServiceForm, CreateDay
from .models import Date, Time, DayOfWeek, Service, RecordingTime, Customer


def home(request):
    return render(request, 'home.html', locals())


def news(request, temp_img=None):
    url = 'https://newsapi.org/v2/everything'
    headers = {
        'X-Api-Key': settings.APIKEY_NEWSAPI
    }

    params = {
        'q': 'car',
        'from': datetime.date.today(),
        'pageSize': 20
    }

    r = requests.get(url=url, params=params, headers=headers)

    data = r.json()
    if data["status"] != "ok":
        return HttpResponse("<h1>Request Failed</h1>")
    data = data["articles"]

    context = {
        "success": True,
        "data": [],
    }

    for i in data:
        time_str = parser.isoparse(i["publishedAt"])
        i["publishedAt"] = time_str.strftime('%A, %d %B %H:%M:%S')

        context["data"].append({
            "title": i["title"],
            "description": "" if i["description"] is None else i["description"],
            "url": i["url"],
            "image": temp_img if i["urlToImage"] is None else i["urlToImage"],
            "publishedat": i["publishedAt"]
        })

    return render(request, 'news.html', context=context)


def user_signup(request):
    error = ''
    if request.method == 'POST':
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            user = user_form.save(commit=False)
            user_form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'You have successfully registered!')
            return redirect('/')
        else:
            messages.error(request, 'Registration error :(')
        context = {
            'user_form': user_form,
            'error': error
        }
    else:
        context = {
            'user_form': UserForm(),
            'error': error
        }
    return render(request, 'signup.html', context)


def user_login(request):
    if request.method == 'POST':
        form = LoginUserForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
        else:
            messages.error(request, 'Wrong username/password!')
        return redirect('/')
    else:
        form = LoginUserForm()

    context = {
        'form': form
    }
    return render(request, 'login.html', context=context)


def user_logout(request):
    logout(request)
    return redirect('/')


def add_service(request):
    recording_time = RecordingTime.objects.all()

    if not request.user.is_authenticated:
        messages.error(request, 'To connect the service you must be authorized!')
        return redirect('/accounts/login/')

    days = DayOfWeek.objects.all()
    if request.method == 'POST':
        form = ServiceForm(request.POST, user=request.user, recording_time=request.POST['recording_time'],
                           working_days=request.POST.getlist('working_days'))
        if form.is_valid():
            with transaction.atomic():
                service_id = form.save()
                Date().create(service_id, create_working_days(request.POST.getlist('working_days')))
                messages.success(request, 'You service is successfully connected')
        else:
            messages.error(request, 'You have entered incorrect data!')
        return redirect('/')
    else:
        form = ServiceForm(user=request.user, recording_time=None, working_days=None)

    context = {
        'form': form,
        'days': days,
        'recording_times': recording_time,
    }
    return render(request, 'add_service.html', context=context)


def create_working_days(list_of_days):
    working_day_indexes = []
    for i in list_of_days:
        day = DayOfWeek.objects.get(pk=i)
        working_day_indexes.append(int(day.index))

    # number of days in a month
    days = calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]

    service_work_days = []
    for i in range(1, days + 1):
        obj = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, i).isoweekday()
        if obj not in working_day_indexes:
            continue
        else:
            service_work_days.append(i)
    return service_work_days


def service_selection(request):
    services = Service.objects.all().order_by('-pk')

    context = {
        'services': services,
    }

    return render(request, 'list_of_services.html', context=context)


def day_selection(request, service_id):
    service = Service.objects.get(pk=service_id)
    day = Date.objects.filter(service_id=service_id).order_by('day')

    # HTML calendar
    list1 = []
    text_calendar = []
    c = calendar.TextCalendar(calendar.MONDAY)
    for i in c.itermonthdays(datetime.datetime.today().year, datetime.datetime.today().month):
        list1.append(i)
    text_calendar.append(list1[:7])
    text_calendar.append(list1[7:14])
    text_calendar.append(list1[14:21])
    text_calendar.append(list1[21:28])
    text_calendar.append(list1[28:35])
    text_calendar.append(list1[35:42])

    # все дни месяца
    all_days = list(filter(lambda num: num != 0, list1))

    # Monthly check
    count_all_days = calendar.monthrange(datetime.datetime.today().year, datetime.datetime.today().month)[1]
    if len(all_days) != count_all_days:
        month_update(request, service_id)

    work_days = []
    for work_day in day:
        if work_day.day < datetime.datetime.today().day:
            continue
        work_days.append(work_day.day)

    context = {
        'all_days': text_calendar,
        'service': service,
        'work_days': work_days
    }

    return render(request, 'day_selection.html', context=context)


def month_update(request, service_id):
    service = Service.objects.get(pk=service_id)
    Date.objects.filter(service_id=service_id)

    index_work_days = []
    for i in service.working_days.all():
        index_work_days.append(i.id)

    create_working_days(request, service_id, index_work_days)
    return messages.success(request, "Schedule updated!")


def time_selection(request, service_id, day_id):
    service = Service.objects.get(pk=service_id)
    day = Date.objects.get(day=day_id, service_id=service_id)
    time = Time.objects.select_related('customer').filter(day_id=day.id, customer_id__isnull=True).order_by('id')
    recording_time = RecordingTime.objects.get(service=service_id)

    if not time.exists():
        Time().add(service, day, recording_time)

    context = {
        'service': service,
        'times': time,
        'day': day,
    }

    return render(request, 'time_selection.html', context=context)


def add_customer(request, service_id, day_id, time_id):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    date = form.save(commit=False)
                    date.save()
                    Time.objects.filter(pk=time_id).update(customer_id=date.id)
                    send_email_to_user(day_id, time_id, service_id)
                    messages.success(request, 'We inform you that the booking was successful!')
                    messages.success(request, 'A confirmation email has been sent to you with all the information.')
            except FailSendMessage:
                messages.error(request, 'Failed to send email. Please repeat again :(')
            except Exception as e:
                messages.error(request, 'A system error has occurred. Please re-register :(')
            return redirect('/')
        else:
            messages.error(request, "Data entered incorrectly!")
        return redirect('/')
    else:
        form = CustomerForm()

    context = {
        'form': form,
    }

    return render(request, 'add_customer.html', context=context)


def send_email_to_user(day_id, time_id, service_id):
    service = Service.objects.get(pk=service_id)
    day = Date.objects.get(pk=day_id)
    time = Time.objects.get(pk=time_id)
    customer = Customer.objects.get(pk=time.customer.id)

    date_record = datetime.date(datetime.datetime.today().year, datetime.datetime.today().month,
                                day.day).strftime('%A, %d %B')
    subject = f'Signing up for an Car Workshop {service.name}'
    message = f'Dear {customer.surname} {customer.name}. \n' \
              f'We inform you that the booking was successful. \n' \
              f'You are signed up for a service at the {service.name} on {date_record} at {time}. \n' \
              f'Adress: {service.address}. \n\n' \
              f'Service Phone number: {service.phone_number} \n' \
              f'Service Email: {service.email} \n\n' \
              f'Sincerely. Service administration'
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [f'{customer.email}'])
    except Exception as e:
        raise FailSendMessage()


class FailSendMessage(Exception):
    """An error occurred while sending the message"""


# views for profile
def profile(request, user_id):
    try:
        service = Service.objects.get(owner_id=user_id)
        days = Date.objects.filter(service_id=service.id, day__in=[i for i in range(datetime.datetime.today().day, 32)])
        times = Time.objects.filter(service_id=service.id,
                                    customer_id__isnull=False,
                                    day_id__in=[i.id for i in days]).order_by('day_id')
        context = {
            'service': service,
            'days': days,
            'times': times
        }
    except ObjectDoesNotExist:
        context = {}

    if not request.user.is_authenticated:
        messages.error(request, 'You do not have permission to view your profile!')
        return redirect('/')

    return render(request, 'view_profile.html', context=context)


def day_add(request, service_id, day_id):
    service = Service.objects.get(pk=service_id)

    Date.objects.create(day=day_id, service_id=service_id)
    messages.success(request, 'Day successfully added as working day!')

    return redirect(service.get_absolute_url())


def day_update(request, service_id, day_id):
    service = Service.objects.get(pk=service_id)
    recording_time = RecordingTime.objects.all()

    if not request.user.is_authenticated and request.user.id != service.owner:
        messages.error(request, 'You do not have permission to perform these actions!')
        return redirect('/')

    if day_id < datetime.datetime.today().day:
        messages.error(request, 'This day cannot be active!')
        return redirect(service.get_absolute_url())

    if request.method == 'POST':
        form = CreateDay(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    day = Date.objects.create(day=day_id, service_id=service_id)
                    recording_time = request.POST['recording_time']
                    opening_time = request.POST['opening_time'] + ':00'
                    closing_time = request.POST['closing_time'] + ':00'

                    if recording_time == '00:30':
                        freq = '0.5H'
                    elif recording_time == '01:00':
                        freq = '1H'
                    time_list = pd.timedelta_range(start=opening_time, end=closing_time, freq=freq).tolist()
                    for i in time_list:
                        Time.objects.create(time=str(i)[7:12], day_id=day.id, service_id=service_id)
                    messages.success(request, "Day successfully added as working day!")
                    return redirect(service.get_absolute_url())
            except DatabaseError:
                messages.error(request, 'Alas. Something went wrong :( Please try again.')
        else:
            messages.error(request, 'Incorrect data entered!')
            return redirect(service.get_absolute_url())
    else:
        form = CreateDay()

    context = {
        'form': form,
        'service': service,
        'day': day_id,
        'times': [],
        'recording_times': recording_time}

    return render(request, 'time_selection.html', context=context)


def day_delete(request, service_id, day_id):
    service = Service.objects.get(pk=service_id)

    if not request.user.is_authenticated and request.user.id != service.owner:
        messages.error(request, 'You do not have permission to perform these actions!')
        return redirect('/')

    try:
        Date.objects.get(pk=day_id).delete()
        messages.success(request, 'Day successfully marked as inactive!')
    except ObjectDoesNotExist:
        messages.error(request, 'An error has occurred. Try again or contact administrator!')

    return redirect(service.get_absolute_url())
