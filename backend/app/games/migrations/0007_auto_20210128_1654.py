# Generated by Django 3.0.11 on 2021-01-28 16:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0006_auto_20210128_1621'),
    ]

    operations = [
        migrations.RenameField(
            model_name='boardgameauthor',
            old_name='board_game',
            new_name='boardgame',
        ),
        migrations.RenameField(
            model_name='boardgamecategory',
            old_name='board_game',
            new_name='boardgame',
        ),
        migrations.RenameField(
            model_name='boardgamemechanic',
            old_name='board_game',
            new_name='boardgame',
        ),
        migrations.RenameField(
            model_name='boardgamepublisher',
            old_name='board_game',
            new_name='boardgame',
        ),
    ]