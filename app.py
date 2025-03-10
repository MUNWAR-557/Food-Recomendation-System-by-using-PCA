from flask import Flask, render_template, request,jsonify,Response
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
from flask import jsonify
import warnings
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF

app = Flask(__name__)
warnings.filterwarnings("ignore", category=Warning)

# Load and preprocess data
default_dataset_path = 'D:\\Downlodes\\sam\\dataset.csv'
raw_data = pd.read_csv(default_dataset_path)
raw_data_frame = pd.DataFrame(raw_data)
raw_data_frame['rating'] = pd.to_numeric(raw_data_frame['rating'], errors='coerce')
raw_data_frame.dropna(inplace=True)
label_encoder = LabelEncoder()
food_rating_encoded = label_encoder.fit_transform(raw_data_frame['rating'])
numeric_columns = ['cost', 'id', 'rating']
numeric_data = raw_data_frame[numeric_columns]

for column in numeric_columns:
    numeric_data[column] = pd.to_numeric(numeric_data[column], errors='coerce')

numeric_data.dropna(inplace=True)
data_scaler = StandardScaler()
scaled_data_frame = data_scaler.fit_transform(numeric_data)

# Sample data for dropdowns
rating_values = sorted(raw_data_frame['rating'].unique(), reverse=True)
city_values = sorted(raw_data_frame['city'].unique(), reverse=False)
cost_values = sorted(raw_data_frame['cost'].unique(), reverse=False)

@app.route('/')
def home(): 
    return render_template('home.html')
 
@app.route('/homes')
def homes(): 
    return render_template('homes.html')

@app.route('/explore')
def explore():
    return render_template('explore.html', rating_values=rating_values, city_values=city_values, cost_values=cost_values)

@app.route('/process_data', methods=['POST'])
def process_data():
    try:
        min_rating = float(request.form.get('min_rating'))
        selected_city = request.form.get('selected_city')
        max_cost = float(request.form.get('max_cost'))
        selected_classifier = request.form.get('selected_classifier')

        filtered_data = raw_data_frame[(raw_data_frame['rating'] >= min_rating) &
                                       (raw_data_frame['city'] == selected_city) &
                                       (raw_data_frame['cost'] <= max_cost)]

        if not filtered_data.empty:
            #Applying PCA 
            pca = PCA(n_components=2)  
            pca_data = pca.fit_transform(scaled_data_frame)

            # Transform filtered data using PCA
            filtered_pca_data = pca.transform(filtered_data[numeric_columns])
            filtered_pca_results = []
            for i, row in enumerate(filtered_data.iterrows()):
                filtered_pca_results.append({
                    "name": row[1]['name'],
                    "rating": row[1]['rating'],
                    "city": row[1]['city'],
                    "cost": row[1]['cost'],
                    "cuisine": row[1]['cuisine'],
                    "address": row[1]['address'],
                    "link": row[1]['link'],
                })

            return render_template('filtered_results.html', filtered_results=filtered_pca_results)

        else:
            return render_template('filtered_results.html', filtered_results=[], selected_classifier=selected_classifier)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/map_view', methods=['GET','POST'])
def map_view():
    return render_template('map_view.html')

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, validators
from flask_wtf.csrf import CSRFProtect


# Initialize CSRF protection and disable it for the entire app
csrf = CSRFProtect(app)
csrf.init_app(app)
app.config['WTF_CSRF_ENABLED'] = False
# Disable Flask sessions
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

# Configure Flask-Mail for Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'sdmunwarali786@gmail.com' 
app.config['MAIL_PASSWORD'] = 'Munwarali@2002'  
mail = Mail(app)

# Define the ContactForm class
class ContactForm(FlaskForm):
    name = StringField('Name', [validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    message = TextAreaField('Message', [validators.DataRequired()])
    submit = SubmitField('Send')

# Contact route with CSRF protection and sessions disabled
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data

        msg = Message('Contact Us Form Submission', sender='sdmunwarali786@gmail.com', recipients=['sdmunwarali786@gmail.com'])
        msg.body = f'Name: {name}\nEmail: {email}\nMessage: {message}'

        try:
            mail.send(msg)
            flash('Message sent successfully!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    return render_template('contact.html', form=form)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
