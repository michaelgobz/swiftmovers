# Generated by Django 3.2.18 on 2023-03-24 14:14

from django.db import migrations
from django.apps import apps as registry
from django.db.models.signals import post_migrate

from .tasks.swiftmovers3_13 import create_full_channel_access_group_task

OPENID_ID = "mirumee.authentication.openidconnect"


def create_full_channel_access_group_for_openid(apps, schema_editor):
    group_name = "OpenID default group"

    def on_migrations_complete(sender=None, **kwargs):
        create_full_channel_access_group_task.delay(group_name)

    PluginConfiguration = apps.get_model("plugins", "PluginConfiguration")
    plugin_conf = PluginConfiguration.objects.filter(
        active=True, identifier=OPENID_ID
    ).first()
    if plugin_conf:
        Group = apps.get_model("account", "Group")
        Group.objects.get_or_create(
            name=group_name, restricted_access_to_channels=False
        )
        update_plugin_default_group_name(plugin_conf, group_name)

        sender = registry.get_app_config("account")
        post_migrate.connect(on_migrations_complete, weak=False, sender=sender)


def update_plugin_default_group_name(plugin_conf, group_name):
    default_group_name_field = "default_group_name_for_new_staff_users"
    for conf in plugin_conf.configuration:
        if conf["name"] == default_group_name_field:
            conf.update([("value", group_name)])
            plugin_conf.save(update_fields=["configuration"])
            return

    group_conf = {"name": default_group_name_field, "value": group_name}
    plugin_conf.configuration.append(group_conf)
    plugin_conf.save(update_fields=["configuration"])


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0078_add_group_channels_conf"),
    ]

    operations = [
        migrations.RunPython(
            create_full_channel_access_group_for_openid,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
