# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-22 05:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workshops', '0117_auto_20160904_0525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventrequest',
            name='admin_fee_payment',
            field=models.CharField(choices=[('NP1', 'Non-profit / non-partner: US$2500'), ('FP1', 'For-profit: US$10,000'), ('self-organized', 'Self-organized: no fee (please let us know if you wish to make a donation)'), ('waiver', 'Waiver requested (please give details in "Anything else")')], default='NP1', max_length=40, verbose_name='Which of the following applies to your payment for the administrative fee?'),
        ),
    ]