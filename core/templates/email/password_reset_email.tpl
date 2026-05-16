{% extends "mail_templated/base.tpl" %}

{% block subject %}
Reset your ToDo password
{% endblock %}

{% block html %}
<p>You requested a password reset. Open the link below and follow the instructions:</p>
<p><a href="{{ reset_link }}">{{ reset_link }}</a></p>
<p>Or send a POST request to <strong>{{ confirm_api_url }}</strong> with JSON:</p>
<pre>{"uid": "...", "token": "...", "new_password": "...", "new_password1": "..."}</pre>
<p>If you did not request this, ignore this email.</p>
{% endblock %}
