from flask import render_template, redirect, url_for
from . import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Add navigation for sales data page
@app.route('/sales')
def sales():
    return redirect(url_for('sales.show_sales'))

# Add navigation for reports page
@app.route('/reports')
def reports():
    return redirect(url_for('sales.reports'))

# Add navigation for visualization page
@app.route('/visualization')
def visualization():
    return redirect(url_for('sales.visualization'))

# Add navigation for regions page
@app.route('/regions')
def regions():
    return redirect(url_for('regions.show_regions'))
