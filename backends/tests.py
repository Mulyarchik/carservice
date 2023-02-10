from django.db import transaction
from django.test import TestCase

# Create your tests here.
from datetime import datetime
from calendar import monthrange

def index1():
    a = 10
    b = 0
    try:
        c = a / b
        print(c)
    except Exception as e:
        print(f'Error {str(e)}')

def index2():

    print("index1")
    index1()
    print("index2")

if __name__ == '__main__':
    index2()

