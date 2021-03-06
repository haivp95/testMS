# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Customer_Feedback(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    username = models.CharField(max_length=250, blank=True, null=True)
    vote = models.FloatField()
    timestamp = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_OPS_MIS_CUSTOMER_FEEDBACK'


class VNPost_Data(models.Model):
    deliveryid = models.CharField(max_length=256)
    itemcode = models.CharField(max_length=256, blank=True, null=True)
    customercode = models.CharField(max_length=256, blank=True, null=True)
    acceptanceposcode = models.CharField(max_length=256, blank=True, null=True)
    toposcode = models.CharField(max_length=256, blank=True, null=True)
    sendingtime = models.CharField(max_length=256, blank=True, null=True)
    deliverytime = models.CharField(max_length=256, blank=True, null=True)
    deliverytimes = models.FloatField(blank=True, null=True)
    receivername = models.CharField(max_length=256, blank=True, null=True)
    inputtime = models.CharField(max_length=256, blank=True, null=True)
    createtime = models.CharField(max_length=256, blank=True, null=True)
    lastupdatetime = models.CharField(max_length=256, blank=True, null=True)
    isdeliverable = models.FloatField(blank=True, null=True)
    isreturn = models.FloatField(blank=True, null=True)
    deliverynote = models.CharField(max_length=500, blank=True, null=True)
    causecode = models.CharField(max_length=256, blank=True, null=True)
    causename = models.CharField(max_length=256, blank=True, null=True)
    solutioncode = models.CharField(max_length=256, blank=True, null=True)
    solutionname = models.CharField(max_length=256, blank=True, null=True)
    datacode = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_OPS_MIS_VNPOST_API'
