import calendar
import datetime

from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import CustomerForm
from .models import Date, Time, Customer
#from config.settings import RECIPIENTS_EMAIL, DEFAULT_FROM_EMAIL
from django.conf import settings

# from .forms import DateForm ####DEFAULT_FROM_EMAIL, RECIPIENTS_EMAIL


def home(request):
    return render(request, 'home.html', locals())


def backends(request):
    total_list = []
    current_month = datetime.datetime.today().month
    current_year = datetime.datetime.today().year

    c = calendar.TextCalendar(calendar.MONDAY)
    for i in c.itermonthdays(current_year, current_month):
        total_list.append(i)

    my_list1 = total_list[:7]
    my_list2 = total_list[7:14]
    my_list3 = total_list[14:21]
    my_list4 = total_list[21:28]
    my_list5 = total_list[35:42]

    total_list = list(filter(lambda num: num != 0, total_list))
    count_date = Date.objects.all().count()
    # в транзакцию !!! Проверка на месяц
    if count_date != len(total_list):
        list_time = []

        for item in range(10, 20 + 1):
            item = str(item)
            item += ':00'
            list_time.append(item)
        Date.objects.all().delete()

        for i in total_list:
            date = Date.objects.create(day=i)
            for j in list_time:
                Time.objects.create(time=j, day=date)

    context = {
        'my_list1': my_list1,
        'my_list2': my_list2,
        'my_list3': my_list3,
        'my_list4': my_list4,
        'my_list5': my_list5,
    }

    return render(request, 'backends.html', context=context)


def choose_time(request, day_id):
    date = Date.objects.get(day=day_id)
    times = Time.objects.all().filter(day_id=date.id).order_by('pk')
    customers = Customer.objects.all()

    context = {
        'times': times,
        'day': date,
        'customers': customers
    }
    return render(request, 'backends2.html', context=context)

def profile(request, day_id, time_id):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            date = form.save(commit=False)
            date.save()
            my_time = Time.objects.filter(pk=time_id)
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
