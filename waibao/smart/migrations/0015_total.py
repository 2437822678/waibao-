# Generated by Django 2.1.5 on 2019-03-04 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smart', '0014_tatol'),
    ]

    operations = [
        migrations.CreateModel(
            name='Total',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('content', models.TextField()),
            ],
        ),
    ]
