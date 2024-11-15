from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

sales = Blueprint('sales', __name__)

# Route to show sales data
@sales.route('/show_sales')
def show_sales():
    connection = get_db()
    query = "SELECT * FROM sales_data"

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    df = pd.DataFrame(result, columns=['sales_data_id', 'monthly_amount', 'date', 'region'])

    # Debugging output to confirm DataFrame structure
    print("Columns in DataFrame:", df.columns)
    print("First few rows of DataFrame:\n", df.head())

    df['Actions'] = df['sales_data_id'].apply(lambda id:
        f'<a href="{url_for("sales.edit_sales_data", sales_data_id=id)}" class="btn btn-sm btn-info">Edit</a> '
        f'<form action="{url_for("sales.delete_sales_data", sales_data_id=id)}" method="post" style="display:inline;">'
        f'<button type="submit" class="btn btn-sm btn-danger">Delete</button></form>'
    )

    table_html = df.to_html(classes='dataframe table table-striped table-bordered', index=False, header=False, escape=False)
    rows_only = table_html.split('<tbody>')[1].split('</tbody>')[0]

    return render_template("sales_data.html", table=rows_only)

# Route to render the add sales data form
@sales.route('/add_sales_data', methods=['GET', 'POST'])
def add_sales_data():
    if request.method == 'POST':
        monthly_amount = request.form['monthly_amount']
        date = request.form['date']
        region = request.form['region']

        connection = get_db()
        query = "INSERT INTO sales_data (monthly_amount, date, region) VALUES (%s, %s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(query, (monthly_amount, date, region))
            connection.commit()

        flash("New sales data added successfully!", "success")
        return redirect(url_for('sales.show_sales'))

    return render_template("add_sales_data.html")

# Route to handle updating a row
@sales.route('/edit_sales_data/<int:sales_data_id>', methods=['GET', 'POST'])
def edit_sales_data(sales_data_id):
    connection = get_db()
    if request.method == 'POST':
        monthly_amount = request.form['monthly_amount']
        date = request.form['date']
        region = request.form['region']

        query = "UPDATE sales_data SET monthly_amount = %s, date = %s, region = %s WHERE sales_data_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (monthly_amount, date, region, sales_data_id))
            connection.commit()

        flash("Sales data updated successfully!", "success")
        return redirect(url_for('sales.show_sales'))

    query = "SELECT * FROM sales_data WHERE sales_data_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (sales_data_id,))
        sales_data = cursor.fetchone()

    return render_template("edit_sales_data.html", sales_data=sales_data)

# Route to handle deleting a row
@sales.route('/delete_sales_data/<int:sales_data_id>', methods=['POST'])
def delete_sales_data(sales_data_id):
    connection = get_db()
    query = "DELETE FROM sales_data WHERE sales_data_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (sales_data_id,))
        connection.commit()

    flash("Sales data deleted successfully!", "success")
    return redirect(url_for('sales.show_sales'))

# Route to generate and display reports
@sales.route('/reports')
def reports():
    connection = get_db()
    query = """
        SELECT 
            sd.sales_data_id, 
            sd.monthly_amount, 
            sd.date, 
            r.region_name AS region
        FROM sales_data sd
        JOIN regions r ON sd.region = r.region_id
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        sales_data = cursor.fetchall()

    # Convert to DataFrame
    df = pd.DataFrame(sales_data)
    print(df['date'])  # Debugging step to inspect raw 'date' values

    # Handle invalid dates
    df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Replace invalid dates with NaT
    df = df.dropna(subset=['date'])  # Drop rows with invalid dates

    # Handle empty DataFrame
    if df.empty:
        return "No data available for reports. Please add sales data and try again."

    # Analysis
    try:
        total_sales_by_region = df.groupby('region')['monthly_amount'].sum().reset_index()
        monthly_sales_trend = df.groupby(df['date'].dt.to_period('M'))['monthly_amount'].sum().reset_index()
        top_region = total_sales_by_region.loc[total_sales_by_region['monthly_amount'].idxmax(), 'region']
    except KeyError as e:
        print(f"KeyError: {e} - DataFrame structure: {df.columns.tolist()}")
        return "Error: Unable to process data for reports. Please check your database and query."

    return render_template(
        'reports.html',
        total_sales_by_region=total_sales_by_region.to_html(classes='table table-striped', index=False),
        monthly_sales_trend=monthly_sales_trend.to_html(classes='table table-striped', index=False),
        top_region=top_region
    )


# Route to generate and display visualizations
@sales.route('/visualization')
def visualization():
    connection = get_db()
    query = """
        SELECT 
            sd.sales_data_id, 
            sd.monthly_amount, 
            sd.date, 
            r.region_name AS region
        FROM sales_data sd
        JOIN regions r ON sd.region = r.region_id
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        sales_data = cursor.fetchall()

    # Convert to DataFrame
    df = pd.DataFrame(sales_data)
    print(df.head())  # Debugging step to inspect the DataFrame

    # Handle empty DataFrame
    if df.empty:
        return "No data available for visualization. Please add sales data and try again."

    # Generate Bar Chart
    try:
        total_sales_by_region = df.groupby('region')['monthly_amount'].sum().reset_index()
        total_sales_by_region['monthly_amount'] = pd.to_numeric(total_sales_by_region['monthly_amount'], errors='coerce')
        print(total_sales_by_region)  # Debugging step to inspect the aggregated data

        fig, ax = plt.subplots()
        total_sales_by_region.plot(kind='bar', x='region', y='monthly_amount', ax=ax)
        ax.set_title('Total Sales by Region')
        ax.set_xlabel('Region')
        ax.set_ylabel('Total Sales')

        # Save plot to a string
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
    except Exception as e:
        print(f"Error during visualization: {e}")
        return "Error generating visualization. Please check your data."

    return render_template('visualization.html', plot_url=plot_url)


