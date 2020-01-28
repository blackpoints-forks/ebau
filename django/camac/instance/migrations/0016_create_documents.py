# Generated by Django 2.2.8 on 2020-01-17 08:47

from django.db import migrations


def migrate_caluma_documents(apps, schema_editor):
    Document = apps.get_model("caluma_form.Document")

    for document in Document.objects.filter(
        **{"meta__camac-instance-id__isnull": False, "form__meta__is-main-form": True}
    ):
        for form in ["sb1", "sb2", "nfd"]:
            if not Document.objects.filter(
                **{
                    "meta__camac-instance-id": document.meta.get("camac-instance-id"),
                    "form_id": form,
                }
            ).exists():
                new_document = Document(
                    form_id=form,
                    created_by_user=document.created_by_user,
                    created_by_group=document.created_by_group,
                    meta={"camac-instance-id": document.meta.get("camac-instance-id")},
                )
                new_document.family = new_document.pk
                new_document.save()


class Migration(migrations.Migration):

    dependencies = [("instance", "0015_instance_service")]

    operations = [migrations.RunPython(migrate_caluma_documents)]