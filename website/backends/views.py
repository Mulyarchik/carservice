import calendar
import datetime

# from config.settings import RECIPIENTS_EMAIL, DEFAULT_FROM_EMAIL
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.mail import send_mail, BadHeaderError
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import CustomerForm, UserForm, LoginUserForm, ServiceForm
from .models import Date, Time, Day_of_week, Service


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


def services(request):
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
    return render(request, 'services.html', context=context)


def list_of_services(request):
    services = Service.objects.all()

    context = {
        'services': services,

    }
    return render(request, 'list_of_services.html', context=context)


def services2(request, service_id):
    service = Service.objects.get(pk=service_id)

    # HTML calendar
    total_list = []
    c = calendar.TextCalendar(calendar.MONDAY)
    for i in c.itermonthdays(datetime.datetime.today().year, datetime.datetime.today().month):
        total_list.append(i)
    my_list1 = total_list[:7]
    my_list2 = total_list[7:14]
    my_list3 = total_list[14:21]
    my_list4 = total_list[21:28]
    my_list5 = total_list[35:42]

    # все дни месяца
    total_list = list(filter(lambda num: num != 0, total_list))

    # рабочие дни недели сервиса
    service_work_days = []
    for i in service.working_days.all():
        for j in str(i):
            service_work_days.append(int(j))

    # все рабочие дни сервиса
    total_work_days = []
    for i in total_list:
        obj = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, i).isoweekday()
        if obj not in service_work_days:
            continue
        else:
            total_work_days.append(i)

    # Проверка на текущий месяц
    count_date = Date.objects.filter(service_id=service_id).count()
    if count_date != len(total_work_days):
        Date.objects.filter(service_id=service_id).delete()
        for i in total_work_days:
            Date.objects.create(day=i, service_id=service_id)

    context = {
        'my_list1': my_list1,
        'my_list2': my_list2,
        'my_list3': my_list3,
        'my_list4': my_list4,
        'my_list5': my_list5,
        'total_work_days': total_work_days,
        'service': service
    }

    return render(request, 'backends.html', context=context)


def services2_time(request, service_id, day_id):
    service = Service.objects.get(pk=service_id)
    day = Date.objects.get(day=day_id, service_id=service_id)
    time = Time.objects.filter(day_id=day.id)

    if not time:
        for item in range(int(str(service.opening_time).split(':00:00')[0]),
                          int(str(service.closing_time).split(':00:00')[0]) + 1):
            item = str(item)
            item += ':00'
            Time.objects.create(time=item, day_id=day.id)

    context = {
        'service': service,
        'times': time,
        'day': day
    }

    return render(request, 'backends2.html', context=context)


def profile2(request, service_id, day_id, time_id):
    # day = Date.objects.get(day=day_id, service_id=service_id)

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            date = form.save(commit=False)
            date.save()
            my_time = Time.objects.get(pk=time_id)
            my_time.update(customer_id=date.id)
            messages.success(request, "Ваша заявка успешно принята!")

            # ___email___
            from_email = request.POST['email']
            name = request.POST['name']
            surname = request.POST['surname']
            for i in my_time:
                my_time = i
            subject = "Заявка на запись в автосервис"

            message = f'Уважаемый {surname} {name}. Вы успешно записались на {my_time}'
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [f'{from_email}'])
            except BadHeaderError:
                return HttpResponse('Ошибка в теме письма.')
            messages.success(request, "Письмо отправлено")
            # ___ ____
            return redirect('/')
        else:
            messages.error(request, "Даннные введены неверно!")
        return redirect('/')
    else:
        form = CustomerForm()

    context = {
        'form': form
    }

    return render(request, 'backends3.html', context=context)


def view_profile(request, user_id):
    # # user = User.objects.get(pk=user_id)
    #
    #  if not request.user.is_authenticated:
    #      messages.error(request, "Вы должны быть авторизованы для просмотра профиля!")
    #      return redirect('/login')
    #
    #  if request.method == "POST":
    #  #    form = UserPhotoUpdate(request.POST, request.FILES, instance=user)
    #      if form.is_valid():
    #          form.save()
    #          messages.success(request, "Изображение пользователя успешно изменено!")
    #      else:
    #          messages.error(request, "Изображение пользователя не было изменено!")
    #      return redirect('/')
    #  else:
    #   #   form = UserPhotoUpdate()

    context = {
        #    'user': user,
        #    'form': form,

    }
    return render(request, 'backends/view_profile.html', context=context)
