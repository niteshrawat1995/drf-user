# Generated by Django 2.0.7 on 2018-07-14 14:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import drf_user.managers
import drfaddons.datatypes


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_date', drfaddons.datatypes.UnixTimestampField(auto_created=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=254, unique=True, verbose_name='Unique UserName')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='EMail Address')),
                ('mobile', models.CharField(max_length=150, unique=True, verbose_name='Mobile Number')),
                ('name', models.CharField(max_length=500, verbose_name='Full Name')),
                ('date_joined', drfaddons.datatypes.UnixTimestampField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=False, verbose_name='Activated')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            managers=[
                ('objects', drf_user.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AuthTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', drfaddons.datatypes.UnixTimestampField(auto_created=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('token', models.TextField(verbose_name='JWT Token passed')),
                ('session', models.TextField(verbose_name='Session Passed')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Authentication Transaction',
                'verbose_name_plural': 'Authentication Transactions',
            },
        ),
        migrations.CreateModel(
            name='OTPValidation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_date', drfaddons.datatypes.UnixTimestampField(auto_created=True)),
                ('otp', models.CharField(max_length=10, unique=True, verbose_name='OTP Code')),
                ('destination', models.CharField(max_length=254, unique=True, verbose_name='Destination Address (Mobile/EMail)')),
                ('create_date', drfaddons.datatypes.UnixTimestampField(auto_now_add=True)),
                ('is_validated', models.BooleanField(default=False, verbose_name='Is Validated')),
                ('validate_attempt', models.IntegerField(default=3, verbose_name='Attempted Validation')),
                ('type', models.CharField(choices=[('email', 'EMail Address'), ('mobile', 'Mobile Number')], default='email', max_length=15, verbose_name='EMail/Mobile')),
                ('send_counter', models.IntegerField(default=0, verbose_name='OTP Sent Counter')),
                ('sms_id', models.CharField(blank=True, max_length=254, null=True, verbose_name='SMS ID')),
                ('reactive_at', drfaddons.datatypes.UnixTimestampField()),
            ],
            options={
                'verbose_name': 'OTP Validation',
                'verbose_name_plural': 'OTP Validations',
            },
        ),
    ]
