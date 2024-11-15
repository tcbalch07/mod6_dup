from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db

regions = Blueprint('regions', __name__)

@regions.route('/regions')
def show_regions():
    connection = get_db()
    query = "SELECT * FROM regions"
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    return render_template('regions.html', regions=result)

@regions.route('/add_region', methods=['GET', 'POST'])
def add_region():
    if request.method == 'POST':
        region_name = request.form['region_name']

        connection = get_db()
        query = "INSERT INTO regions (region_name) VALUES (%s)"
        with connection.cursor() as cursor:
            cursor.execute(query, (region_name,))
            connection.commit()

        flash("Region added successfully!", "success")
        return redirect(url_for('regions.show_regions'))
    return render_template('add_region.html')

@regions.route('/edit_region/<int:region_id>', methods=['GET', 'POST'])
def edit_region(region_id):
    connection = get_db()
    if request.method == 'POST':
        region_name = request.form['region_name']

        query = "UPDATE regions SET region_name = %s WHERE region_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (region_name, region_id))
            connection.commit()

        flash("Region updated successfully!", "success")
        return redirect(url_for('regions.show_regions'))

    query = "SELECT * FROM regions WHERE region_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (region_id,))
        region = cursor.fetchone()

    return render_template('edit_region.html', region=region)

@regions.route('/delete_region/<int:region_id>', methods=['POST'])
def delete_region(region_id):
    connection = get_db()
    query = "DELETE FROM regions WHERE region_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (region_id,))
        connection.commit()

    flash("Region deleted successfully!", "success")
    return redirect(url_for('regions.show_regions'))
