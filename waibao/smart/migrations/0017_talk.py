# Generated by Django 2.1.5 on 2019-03-14 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smart', '0016_talks'),
    ]

    operations = [
        migrations.CreateModel(
            name='Talk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=64)),
                ('content', models.TextField(null=True)),
            ],
        ),
    ]
