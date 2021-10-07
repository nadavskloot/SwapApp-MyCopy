# Generated by Django 3.0.3 on 2020-05-06 01:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tradeboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='default_profile.png', upload_to='profile_pics')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
        ),
        migrations.CreateModel(
            name='MessageChain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messagechain_buying', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tradeboard.Post')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messagechain_selling', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Message-Chain',
                'verbose_name_plural': 'Message-Chains',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=1000)),
                ('time_sent', models.DateTimeField(default=django.utils.timezone.now)),
                ('message_type', models.CharField(choices=[('Text', 'Text'), ('Offer', 'Offer')], max_length=10)),
                ('chain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='users.MessageChain')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages_recieved', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages_sent', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
        ),
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posts', models.ManyToManyField(to='tradeboard.Post')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bookmark', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Wishlist',
                'verbose_name_plural': 'Wishlists',
            },
        ),
    ]
