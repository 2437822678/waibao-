# Generated by Django 2.1.5 on 2019-03-03 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smart', '0009_person'),
    ]

    operations = [
        migrations.CreateModel(
            name='Buzzword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=64)),
            ],
        ),
    ]
