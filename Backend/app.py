from flask import Flask, render_template, request, redirect, url_for
import pymysql
from jinja2 import BaseLoader, TemplateNotFound
import requests

app = Flask(__name__)

class RemoteLoader(BaseLoader):
    def get_source(self, environment, template):
        url = f'http://18.207.235.183/templates/{template}'
        print(f"Fetching template from: {url}")  # Debug statement
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Template fetched successfully: {url}")  # Debug statement
                return response.text, url, lambda: True
            else:
                print(f"Failed to fetch template: {response.status_code} - {response.text}")
                raise TemplateNotFound(template)
        except Exception as e:
            print(f"Error fetching template: {e}")  # Debug statement
            raise TemplateNotFound(template)

app.jinja_loader = RemoteLoader()

def get_db_connection():
    return pymysql.connect(
        host='database-1.cba8egc8q545.us-east-1.rds.amazonaws.com',
        user='admin',
        password='Admin123',
        db='employees',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        data = request.form
        if 'edit' in request.form:
            id = data['id']
            cursor.execute('SELECT * FROM employees WHERE id = %s', (id,))
            employee = cursor.fetchone()
            cursor.close()
            conn.close()
            return render_template('index.html', employees=[], employee=employee, mode='edit')

        elif 'update' in request.form:
            id = data['id']
            cursor.execute('UPDATE employees SET first_name = %s, last_name = %s, date_joined = %s, tasks_given = %s, tasks_completed = %s WHERE id = %s',
                           (data['first_name'], data['last_name'], data['date_joined'], data['tasks_given'], data['tasks_completed'], id))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index'))

    cursor.execute('SELECT * FROM employees')
    employees = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', employees=employees, mode='view')

@app.route('/insert', methods=['POST'])
def insert():
    data = request.form
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO employees (id, first_name, last_name, date_joined, tasks_given, tasks_completed) VALUES (%s, %s, %s, %s, %s, %s)',
                   (data['id'], data['first_name'], data['last_name'], data['date_joined'], data['tasks_given'], data['tasks_completed']))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT * FROM employees WHERE id = %s', (id,))
        employee = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('index.html', employees=[], employee=employee, mode='edit')

    elif request.method == 'POST':
        data = request.form
        cursor.execute('UPDATE employees SET first_name = %s, last_name = %s, date_joined = %s, tasks_given = %s, tasks_completed = %s WHERE id = %s',
                       (data['first_name'], data['last_name'], data['date_joined'], data['tasks_given'], data['tasks_completed'], id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
