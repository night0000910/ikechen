# Generated by Django 3.2.7 on 2024-09-27 07:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Coordinate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=20)),
                ('image', models.ImageField(upload_to='images/coordinates')),
            ],
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Mentor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='unknown', max_length=10)),
                ('profile_image', models.ImageField(default='mentorapp/images/profile_image.png', upload_to='images/mentor_profiles')),
                ('self_introduction', models.CharField(default='', max_length=300)),
                ('coordinate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mentorapp.coordinate')),
                ('style', models.ManyToManyField(to='mentorapp.Style')),
            ],
        ),
    ]
