import os

# Create templates directory if it doesn't exist
if not os.path.exists('templates/auth'):
    os.makedirs('templates/auth')

# Create login.html
with open('templates/auth/login.html', 'w') as f:
    f.write('''{% extends "base.html" %}

{% block title %}Login{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card">
                <div class="card-header">
                    <h4>Login</h4>
                </div>
                <div class="card-body">
                    <form method="POST">
                        {{ form.hidden_tag() }}
                        
                        <div class="mb-3">
                            {{ form.username.label(class="form-label") }}
                            {{ form.username(class="form-control") }}
                            {% for error in form.username.errors %}
                                <div class="text-danger">{{ error }}</div>
                            {% endfor %}
                        </div>
                        
                        <div class="mb-3">
                            {{ form.password.label(class="form-label") }}
                            {{ form.password(class="form-control") }}
                            {% for error in form.password.errors %}
                                <div class="text-danger">{{ error }}</div>
                            {% endfor %}
                        </div>
                        
                        <div class="mb-3 form-check">
                            {{ form.remember_me(class="form-check-input") }}
                            {{ form.remember_me.label(class="form-check-label") }}
                        </div>
                        
                        {{ form.submit(class="btn btn-primary") }}
                    </form>
                    
                    <div class="mt-3">
                        <p>Don't have an account? <a href="{{ url_for('auth.register') }}">Register here</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')

# Create register.html
with open('templates/auth/register.html', 'w') as f:
    f.write('''{% extends "base.html" %}

{% block title %}Register{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card">
                <div class="card-header">
                    <h4>Register</h4>
                </div>
                <div class="card-body">
                    <form method="POST">
                        {{ form.hidden_tag() }}
                        
                        <div class="mb-3">
                            {{ form.username.label(class="form-label") }}
                            {{ form.username(class="form-control") }}
                            {% for error in form.username.errors %}
                                <div class="text-danger">{{ error }}</div>
                            {% endfor %}
                        </div>
                        
                        <div class="mb-3">
                            {{ form.email.label(class="form-label") }}
                            {{ form.email(class="form-control") }}
                            {% for error in form.email.errors %}
                                <div class="text-danger">{{ error }}</div>
                            {% endfor %}
                        </div>
                        
                        <div class="mb-3">
                            {{ form.password.label(class="form-label") }}
                            {{ form.password(class="form-control") }}
                            {% for error in form.password.errors %}
                                <div class="text-danger">{{ error }}</div>
                            {% endfor %}
                        </div>
                        
                        <div class="mb-3">
                            {{ form.password2.label(class="form-label") }}
                            {{ form.password2(class="form-control") }}
                            {% for error in form.password2.errors %}
                                <div class="text-danger">{{ error }}</div>
                            {% endfor %}
                        </div>
                        
                        {{ form.submit(class="btn btn-primary") }}
                    </form>
                    
                    <div class="mt-3">
                        <p>Already have an account? <a href="{{ url_for('auth.login') }}">Login here</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')

print("Auth templates created successfully!")