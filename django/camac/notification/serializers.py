import itertools
from collections import namedtuple
from html import escape

import inflection
import jinja2
from django.core.mail import EmailMessage
from rest_framework import exceptions
from rest_framework_json_api import serializers

from camac.core.models import Activation
from camac.instance.mixins import InstanceEditableMixin
from camac.instance.models import Instance
from camac.user.models import Service

from . import models

MERGE_DATE_FORMAT = '%d.%m.%Y'


class ActivationMergeSerializer(serializers.Serializer):
    deadline_date = serializers.DateTimeField(format=MERGE_DATE_FORMAT)
    start_date = serializers.DateTimeField(format=MERGE_DATE_FORMAT)
    end_date = serializers.DateTimeField(format=MERGE_DATE_FORMAT)
    circulation_state = serializers.StringRelatedField()
    service = serializers.StringRelatedField()
    reason = serializers.CharField()
    circulation_answer = serializers.StringRelatedField()
    # TODO add notices (static SerializerMethodField mapping)


class BillingEntryMergeSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    service = serializers.StringRelatedField()
    created = serializers.DateTimeField(format=MERGE_DATE_FORMAT)
    account = serializers.SerializerMethodField()
    account_number = serializers.SerializerMethodField()

    def get_account(self, billing_entry):
        billing_account = billing_entry.billing_account
        return "{0} / {1}".format(
            billing_account.department, billing_account.name
        )

    def get_account_number(self, billing_entry):
        return billing_entry.billing_account.account_number


class InstanceMergeSerializer(serializers.Serializer):
    """Converts instance into a dict to be used with template merging."""

    # TODO: document.Template and notification.NotificationTemplate should
    # be moved to its own app template including this serializer.

    location = serializers.StringRelatedField()
    identifier = serializers.CharField()
    activations = ActivationMergeSerializer(many=True)
    billing_entries = BillingEntryMergeSerializer(many=True)

    def __init__(self, instance, *args, escape=False, **kwargs):
        self.escape = escape
        instance.activations = Activation.objects.filter(
            circulation__instance=instance
        )
        super().__init__(instance, *args, **kwargs)

    def _escape(self, data):
        result = data
        if isinstance(data, str):
            result = escape(data)
        elif isinstance(data, list):
            result = [self._escape(value) for value in data]
        elif isinstance(data, dict):
            result = {key: self._escape(value) for key, value in data.items()}

        return result

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        for field in instance.fields.all():
            name = inflection.underscore('field-' + field.name)
            ret[name] = field.value

        if self.escape:
            ret = self._escape(ret)

        return ret


class NotificationTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.NotificationTemplate
        fields = (
            'purpose',
            'subject',
            'body',
        )


class NotificationTemplateMergeSerializer(InstanceEditableMixin,
                                          serializers.Serializer):
    instance = serializers.ResourceRelatedField(
        queryset=Instance.objects.all()
    )
    subject = serializers.CharField(required=False)
    body = serializers.CharField(required=False)

    def _merge(self, value, instance):
        try:
            value_template = jinja2.Template(value)
            data = InstanceMergeSerializer(instance).data
            return value_template.render(data)
        except jinja2.TemplateError as e:
            raise exceptions.ValidationError(str(e))

    def validate(self, data):
        notification_template = self.context['view'].get_object()
        instance = data['instance']

        data['subject'] = self._merge(
            data.get('subject', notification_template.subject),
            instance
        )
        data['body'] = self._merge(
            data.get('body', notification_template.body),
            instance
        )
        data['pk'] = '{0}-{1}'.format(
            notification_template.pk, instance.pk
        )

        return data

    def create(self, validated_data):
        NotificationTemplateMerge = namedtuple(
            'NotificationTemplateMerge', validated_data.keys()
        )
        obj = NotificationTemplateMerge(**validated_data)

        return obj

    class Meta:
        resource_name = 'notification-template-merges'


class NotificationTemplateSendmailSerializer(
    NotificationTemplateMergeSerializer
):
    recipient_types = serializers.MultipleChoiceField(
        choices=('applicant', 'municipality', 'service')
    )

    def _get_recipients_applicant(self, instance):
        return [instance.user.email]

    def _get_recipients_municipality(self, instance):
        return [instance.group.email]

    def _get_recipients_service(self, instance):
        services = Service.objects.filter(
            pk__in=instance.circulations.values('activations__service')
        )

        return [
            service.email
            for service in services
        ]

    def create(self, validated_data):
        instance = validated_data['instance']
        recipients = itertools.chain(*[
            getattr(self, '_get_recipients_%s' % recipient_type)(instance)
            for recipient_type in validated_data['recipient_types']
        ])

        email = EmailMessage(
            subject=validated_data['subject'],
            body=validated_data['body'],
            bcc=set(recipients)
        )

        return email.send()

    class Meta:
        resource_name = 'notification-template-sendmails'
