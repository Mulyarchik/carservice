import calendar
import datetime

# from config.settings import RECIPIENTS_EMAIL, DEFAULT_FROM_EMAIL
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, BadHeaderError
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import CustomerForm, UserForm, LoginUserForm, ServiceForm
from .models import Date, Time, Day_of_week, Service

remote_days = []


def home(request):
    return render(request, 'home.html', locals())


def user_signup(request):
    error = ''
    if request.method == 'POST':
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            user = user_form.save(commit=False)
            user_form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Вы успешно зарегестрировались")
            return redirect('/')
        else:
            messages.error(request, "Ошибка регистрации")
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
            messages.error(request, "Неправильное имя пользователя/пароль!")
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


@login_required
def add_service(request):
    days = Day_of_week.objects.all()

    if request.method == 'POST':
        form = ServiceForm(data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                data = form.save(commit=False)
                data.owner = request.user
                data.save()

                list_of_days = request.POST.getlist('working_days')
                for day in list_of_days:
                    days = Day_of_week.objects.get(pk=day)
                    data.working_days.add(days)
        else:
            messages.error(request, "Вы указали неверные данные!")
        return redirect('/')
    else:
        form = ServiceForm()

    context = {
        'form': form,
        'days': days,
    }
    return render(request, 'add_service.html', context=context)


def service_selection(request):
    services = Service.objects.all()

    context = {
        'services': services,

    }
    return render(request, 'list_of_services.html', context=context)


def day_selection(request, service_id):
    service = Service.objects.get(pk=service_id)

    # HTML calendar
    total_list = []
    slice_list = []
    c = calendar.TextCalendar(calendar.MONDAY)
    for i in c.itermonthdays(datetime.datetime.today().year, datetime.datetime.today().month):
        total_list.append(i)
    slice_list.append(total_list[:7])
    slice_list.append(total_list[7:14])
    slice_list.append(total_list[14:21])
    slice_list.append(total_list[21:28])
    slice_list.append(total_list[35:42])

    # все дни месяца
    total_list = list(filter(lambda num: num != 0, total_list))

    # рабочие дни недели сервиса
    service_work_days = []
    for i in service.working_days.all():
        service_work_days.append(i.id)

    # все рабочие дни сервиса
    total_work_days = []
    for i in total_list:
        if i < datetime.datetime.today().day:
            continue
        obj = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, i).isoweekday()
        if obj not in service_work_days:
            continue
        else:
            total_work_days.append(i)

    for remote_day in remote_days:
        if remote_day[1] == service.id:
            try:
                total_work_days.remove(remote_day[0])
            except ValueError:
                print(f'нет обьекта для удаления')

    # Проверка на текущий месяц
    count_date = Date.objects.filter(service_id=service_id).count()
    if count_date - len(remote_days) != len(total_work_days):
        Date.objects.filter(service_id=service_id).delete()
        for i in total_work_days:
            Date.objects.create(day=i, service_id=service_id)

    context = {
        'total_list': slice_list,
        'total_work_days': total_work_days,
        'service': service,
    }

    return render(request, 'day_selection.html', context=context)


def time_selection(request, service_id, day_id):
    service = Service.objects.get(pk=service_id)
    day = Date.objects.get(day=day_id, service_id=service_id)
    time = Time.objects.select_related('customer').filter(day_id=day.id).order_by('id')

    if not Time.objects.filter(day_id=day.id):
        for item in range(int(str(service.opening_time).split(':00:00')[0]),
                          int(str(service.closing_time).split(':00:00')[0]) + 1):
            item = str(item)
            item += ':00'
            Time.objects.create(time=item, day_id=day.id, service_id=service_id)

    context = {
        'service': service,
        'times': time,
        'day': day
    }

    return render(request, 'time_selection.html', context=context)


def add_customer(request, service_id, day_id, time_id):
    service = Service.objects.get(pk=service_id)
    day = Date.objects.get(pk=day_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            date = form.save(commit=False)
            date.save()
            my_time = Time.objects.filter(pk=time_id)
            my_time.update(customer_id=date.id)
            messages.success(request, "We inform you that the booking was successful!")

            # _____email_____
            from_email = request.POST['email']
            name = request.POST['name']
            surname = request.POST['surname']
            for i in my_time:
                my_time = i
            date_record = datetime.date(datetime.datetime.today().year, datetime.datetime.today().month,
                                        day.day).strftime('%A, %d %B')
            subject = f"Signing up for an Car Workshop {service.name}"
            message = f'Dear {surname} {name}. \n' \
                      f'We inform you that the booking was successful. \n' \
                      f'You are signed up for a service at the {service.name} on {date_record} at {my_time}. \n' \
                      f'Adress: {service.address}. \n\n' \
                      f'Phone number: {service.phone_number}. \n' \
                      f'Email: {service.email}. \n'
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [f'{from_email}'])
            except BadHeaderError:
                return HttpResponse('Ошибка в теме письма.')
            messages.success(request, "A confirmation email has been sent to you with all the information.")
            # ___________
            return redirect('/')
        else:
            messages.error(request, "Даннные введены неверно!")
        return redirect('/')
    else:
        form = CustomerForm()

    context = {
        'form': form
    }

    return render(request, 'add_customer.html', context=context)


# views for profile
def profile(request, user_id):
    service = Service.objects.get(owner_id=user_id)
    days = Date.objects.filter(service_id=service.id)
    times = Time.objects.filter(service_id=service.id)

    if not request.user.is_authenticated:
        messages.error(request, "You do not have permission to view your profile!")
        return redirect('/')

    context = {
        'service': service,
        'days': days,
        'times': times
    }

    return render(request, 'view_profile.html', context=context)


def day_update(request, service_id, day_id):
    service = Service.objects.get(pk=service_id)

    if not request.user.is_authenticated and request.user.id != service.owner:
        messages.error(request, "You do not have permission to perform these actions!")
        return redirect('/')

    try:
        Date.objects.get(day=day_id, service_id=service_id)
        day = Date.objects.get(day=day_id, service_id=service_id)
        time = Time.objects.select_related('customer').filter(day_id=day.id).order_by('id')
        context = {
            'service': service,
            'days': day,
            'times': time, }

    except ObjectDoesNotExist:
        context = {
            'service': service,
            'times': []}

    return render(request, 'time_selection.html', context=context)


def day_delete(request, service_id, day_id):
    global remote_days
    my_list = [day_id, service_id]
    remote_days.append(my_list)

    service = Service.objects.get(pk=service_id)

    if not request.user.is_authenticated and request.user.id != service.owner:
        messages.error(request, "You do not have permission to perform these actions!")
        return redirect('/')

    try:
        Date.objects.get(day=day_id, service_id=service_id).delete()
        messages.success(request, "Day successfully marked as inactive!")
    except ObjectDoesNotExist:
        messages.error(request, "An error has occurred. Try again or contact administrator!")

    return day_selection(request, service_id)
