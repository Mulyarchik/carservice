# Django CarService #

web service based on Django web framework. The "CarService" allows you to connect different service stations with a
unique
work schedule.
And also allows ordinary users to make an appointment at a convenient time for a visit to get their car serviced.

# Built on #

* Django 4.1
* Python 3.10


# Getting started #

Clone the repository and enter into it.

```
$ git clone https://github.com/Mulyarchik/carservice.git
$ cd carservice
```

Set your settings in the ‘.env’ file, but defaults is enough just to try the service locally.

Run docker compose to build and run the service and it’s dependencies.

```
$ docker compose up -d --build
```

Optionally you can populate your database with some dummy data.

```
$ docker compose exec web python manage.py setup_test_data
```

Open in your browser:

```
http://localhost:8080/
```


# Business processes: #

![image](assets/business_processes.drawio.png)

# ERD: #

![image](assets/erd.drawio.png)

# Screenshots #

Want to see the interface of the site? Check it out!

|                                ![](assets/home.png) Homepage                                 |                     ![](assets/news.png)   News page(shows 20 latest current news)                     | ![](assets/all_services.png)    Service catalog and the ability to connect your own service |
|:--------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------:|
|                      ![](assets/add_service.png)    Adding your service                      |                   ![](assets/pick_date_via_owner.png)    Pick date via service owner                   |                 ![](assets/pick_date_via_user.png)   Pick date via visitor                  |
|        ![](assets/pick_time_via_visitor.png)   Picking a convenient time via visitor         |                     ![](assets/leaving_an_application.png)  Leaving an application                     |                            ![](assets/email.png)   Email to user                            |
| ![](assets/pick_time_from_work_day_via_owner.png)  Time selection through the service author | ![](assets/mark_day_as_working_day.png)  Time selection for non-working day through the service author |      ![](assets/profile_with_connect_service.png)  View profile with connected service      |