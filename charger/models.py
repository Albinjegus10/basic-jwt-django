
from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    attached_file = models.FileField(upload_to='uploads/', null=True, blank=True)

    def __str__(self):
        return self.title


# models.py

from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    publication_date = models.DateField()
    fff=models.ManyToOneRel
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')

    def __str__(self):
        return self.title

from django.db import models

class Book2(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.title


from django.db import models


class Item(models.Model):
    category = models.CharField(max_length=255)
    subcategory = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()

    def __str__(self) -> str:
        return self.name
