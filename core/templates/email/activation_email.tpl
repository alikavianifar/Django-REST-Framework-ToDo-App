{% extends "mail_templated/base.tpl" %}

{% block subject %}
Activate your ToDo account
{% endblock %}

{% block html %}
<p>Click the link below to activate your account:</p>
<p><a href="{{ activation_link }}">{{ activation_link }}</a></p>
<p>If you did not register, you can ignore this email.</p>
{% endblock %}
