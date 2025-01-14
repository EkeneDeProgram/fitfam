import re
import matplotlib
matplotlib.use('Agg')
from flask import redirect, session
from functools import wraps
import base64
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io

# Constant for converting cm to meters
CM_TO_METERS = 100

# Constant for physically active water intake (40-45 ml per kg)
AVG_WATER_ML_PER_KG = 40

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def validate_username(username, messages):
    if not username:
        messages.append(("danger", "Username is required."))
    elif not re.match(r'^[A-Za-z0-9]+$', username):
        messages.append(("danger", "Username must contain only characters and numbers."))
    return messages

def validate_email(email, messages):
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not email:
        messages.append(("danger", "Email is required."))
    elif not re.match(email_pattern, email) or "@" not in email or "." not in email:
        messages.append(("danger", "Please enter a valid email address."))
    return messages


def validate_confirmation_password(password, confirmation, messages):
    if not confirmation:
        messages.append(("danger", "Confirmation password is required."))
    elif password != confirmation:
        messages.append(("danger", "Passwords do not match."))
    return messages

def validate_password(password, messages):
    if not password:
        messages.append(("danger", "Password is required."))
    elif len(password) < 8:
        messages.append(("danger", "Password must be at least 8 characters long."))
    elif not any(char.isupper() for char in password):
        messages.append(("danger", "Password must contain at least 1 uppercase letter."))
    elif not any(char.islower() for char in password):
        messages.append(("danger", "Password must contain at least 1 lowercase letter."))
    elif not any(char.isdigit() for char in password):
        messages.append(("danger", "Password must contain at least 1 number."))
    elif not any(char in "!@#$%^&*()_+-=[]{};':\"\\|,.<>/? " for char in password):
        messages.append(
            ("danger", "Password must contain at least one special character (!@#$%^&*()_+-=[]{};':\"\\|,.<>/?).")
        )
    
    return messages


def validate_contact_inputs(field_value, field_name, messages):
    if not field_value:
        messages.append(("danger", f"{field_name} is required."))

def calculate_bmi(weight_kg, height_cm):
    # Convert height from cm to meters
    height_meters = height_cm / CM_TO_METERS
    body_mass_index = weight_kg / (height_meters ** 2)
    return round(body_mass_index, 1)


def calculate_bmi_by_activity(user_data):
    bmi_data = [
        round(activity.weight / ((activity.height / CM_TO_METERS) ** 2), 1)
        for activity in user_data
    ]
    return bmi_data


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Healthy Weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"
    
def calculate_healthy_weight_range(height_cm):
    if height_cm is None:
        return None
    
    height_m = height_cm / 100
    lower_bound = 18.5 * (height_m ** 2)
    upper_bound = 24.9 * (height_m ** 2)
    return round(lower_bound, 1), round(upper_bound, 1)

# def get_distinct_user_activity_data(db, user_id):
#     return db.execute("SELECT DISTINCT age, gender FROM activities WHERE user_id = ?", user_id)

def get_age_and_gender(distinct_user_activity_data):
    if distinct_user_activity_data:
        age = distinct_user_activity_data[0]["age"]
        gender = distinct_user_activity_data[0]["gender"].capitalize()
    else:
        age = None
        gender = None
    return age, gender


def get_latest_user_water_intake(latest_user_activity):
    if latest_user_activity:
        user_water_intake = latest_user_activity["water_intake"]
    else:
        user_water_intake = None
    return user_water_intake

def get_latest_weight_and_height(latest_user_activity):
    if latest_user_activity:
        weight_kg = latest_user_activity["weight"]
        height_cm = latest_user_activity["height"]
    else:
        weight_kg = None
        height_cm = None
    return weight_kg, height_cm



def calculate_daily_water_intake(latest_user_activity):
    if latest_user_activity:
        weight_kg = latest_user_activity.weight
        daily_water_intake = (AVG_WATER_ML_PER_KG * weight_kg) / 1000
    else:
        daily_water_intake = None
    return daily_water_intake


def calculate_weight_difference(user_activities):
    if len(user_activities) >= 2:
        latest_weight = user_activities[0].weight
        second_latest_weight = user_activities[1].weight
        weight_difference = latest_weight - second_latest_weight
    elif len(user_activities) == 1:
        latest_weight = user_activities[0].weight
        second_latest_weight = 0
        weight_difference = 0
    else:
        weight_difference = 0
    
    return weight_difference


def calculate_bmi_and_category(weight_kg, height_cm):
    if weight_kg and height_cm:
        bmi = calculate_bmi(weight_kg, height_cm)
        bmi_category_result = bmi_category(bmi)
    else:
        bmi = None
        bmi_category_result = None
    return bmi, bmi_category_result


def extract_weight_and_dates(user_data):
    weight_data = [data.weight for data in user_data]
    registered_at_data = [data.registered_at for data in user_data]
    return weight_data, registered_at_data

def create_dataframe(weight_data, registered_at_data):
    df = pd.DataFrame({
        'weight': weight_data,
        'registered_at': registered_at_data
    })
    return df

def generate_weight_plot(df):
    sns.set(style='ticks', font_scale=0.6, rc={'axes.facecolor': '#E6E6FA'})
    plt.figure(figsize=(6, 4))
    g = sns.lineplot(x='registered_at', y='weight', data=df, linewidth=4)
    g.lines[0].set_linestyle('-')
    g.lines[0].set_color('#800080')
    g.lines[0].set_markerfacecolor('blue')
    g.lines[0].set_markeredgecolor('black')
    g.lines[0].set_markersize(8)
    
    plt.xlabel('Date', fontweight='bold', color='#800080', fontsize=10)
    plt.ylabel('Weight (kg)', fontweight='bold', color='#800080', fontsize=10)
    plt.title('Weight Progression', fontweight='bold', color='#800080', fontsize=16)
    plt.xticks(rotation=45)

    # Format the x-axis date using DateFormatter
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # Set x-tick labels to an empty string to hide the date values
    plt.gca().set_xticklabels([])

    # Automatically adjust subplot parameters to prevent overlapping elements
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    plot_data = base64.b64encode(buffer.read()).decode('utf-8')
    return plot_data

def create_weight_plot(user_data):
    if not user_data:
        return None

    weight_data, registered_at_data = extract_weight_and_dates(user_data)
    df = create_dataframe(weight_data, registered_at_data)
    plot_data = generate_weight_plot(df)

    return plot_data

def create_bmi_dataframe(bmi_data, registered_at_data):
    df = pd.DataFrame({
        'bmi': bmi_data,
        'registered_at': registered_at_data
    })
    return df

def generate_bmi_plot(df):
    sns.set(style='ticks', font_scale=0.6, rc={'axes.facecolor': '#E6E6FA'})

    plt.figure(figsize=(6, 4))
    g = sns.lineplot(x='registered_at', y='bmi', data=df, linewidth=4)
    g.lines[0].set_linestyle('-')
    g.lines[0].set_color('#800080')
    g.lines[0].set_markerfacecolor('red')
    g.lines[0].set_markeredgecolor('black')
    g.lines[0].set_markersize(8)

    plt.xlabel('Date', fontweight='bold', color='#800080', fontsize=10)
    plt.ylabel('BMI', fontweight='bold', color='#800080', fontsize=10)
    plt.title('BMI Progression', fontweight='bold', color='#800080', fontsize=16)
    plt.xticks(rotation=45)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().set_xticklabels([])
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    plot_data = base64.b64encode(buffer.read()).decode('utf-8')
    return plot_data



def create_bmi_plot(user_data):
    if not user_data:
        return None

    # Calculate BMI data
    bmi_data = calculate_bmi_by_activity(user_data)
    
    # Extract registered_at data using dot notation
    registered_at_data = [activity.registered_at for activity in user_data]

    # Create DataFrame
    df = create_bmi_dataframe(bmi_data, registered_at_data)
    
    # Generate plot
    plot_data = generate_bmi_plot(df)

    return plot_data


def get_latest_bodyfat_and_bodymass(latest_user_activity):
    if latest_user_activity:
        body_fat_percentage = latest_user_activity["body_fat_percentage"]
        muscle_mass = latest_user_activity["muscle_mass"]
    else:
        body_fat_percentage = None
        muscle_mass = None
    return body_fat_percentage, muscle_mass