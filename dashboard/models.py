#
# Copyright (c) 2020. Betterworks, Inc. All Rights Reserved.
#
# Author: adithya.bhat@gmail.com (Adithya bhat)
#
# This module has all the database models
# Sample usage
# Get object
# <model_name>.objects.get(pk=<primary_key>)
# Filter object
# <model_name>.objects.filter(<filter_condition>)
# Delete object
# <model_name>.objects.filter(<filter_condition>).delete()
# Create object
# <model_name>.objects.create(**fields)
from django.db import models

# Create your models here.

class Department(models.Model):
    department_id = models.CharField(primary_key=True ,max_length=15)
    name = models.CharField(max_length=15, null=True, unique=True)
    location = models.CharField(max_length=20, null=True)
    date_of_innaugration = models.DateField(null=True)
    class Meta:
        db_table = "department"

class Teams(models.Model):
    team_id = models.CharField(primary_key=True ,max_length=15)
    team_lead_id = models.ForeignKey('Users', on_delete=models.CASCADE, null=True)
    department_id = models.ForeignKey('Department', on_delete=models.CASCADE, null=True)
    average_pay = models.CharField(max_length=10, null=True)
    class Meta:
        db_table = "teams"
        
class Users(models.Model):
    user_id = models.CharField(primary_key=True ,max_length=15)
    first_name = models.CharField(max_length=25, null=True)
    last_name = models.CharField(max_length=25, null=True)
    team_id = models.ForeignKey('Teams', on_delete=models.CASCADE, null=True)
    class Meta:
        db_table = "users"

class Objectives(models.Model):
    objective_id = models.CharField(primary_key=True ,max_length=12)
    user_id = models.ForeignKey('Users', on_delete=models.CASCADE)
    objective_text = models.CharField(max_length=100, null=True)
    class Meta:
        db_table = "objectives"

class KeyResults(models.Model):
    STATUSES = (("Pending", "PENDING"), ("Complete", "COMPLETE"))
    keyresult_id = models.CharField(primary_key=True ,max_length=12)
    objective_id = models.ForeignKey('Objectives', on_delete=models.CASCADE, null=True)
    keyresult_text = models.CharField(max_length=100, null=True)
    status =  models.CharField(max_length=12, choices=STATUSES, null=True)
    due_date = models.DateField(null=True)
    updated_date = models.DateField(null=True)
    class Meta:
        db_table = "keyresults"