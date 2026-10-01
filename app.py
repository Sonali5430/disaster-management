from flask import Flask, render_template, request
import oracledb

app = Flask(__name__)

# Oracle Database Connection
connection = oracledb.connect(
    user="system",
    password="Sonali@5430",
    dsn="localhost/XE"
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/victim', methods=['GET', 'POST'])
def victim():

    if request.method == 'POST':

        print("Form Submitted")

        victim_id = request.form['victim_id']
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        contact = request.form['contact']
        location_id = request.form['location_id']

        try:

            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO Victim
                VALUES(:1,:2,:3,:4,:5,:6)
            """, (
                victim_id,
                name,
                age,
                gender,
                contact,
                location_id
            ))

            connection.commit()
            
            print("Data Inserted Successfully")

            return "Victim Registered Successfully"

        except Exception as e:

            return f"Database Error: {e}"

    return render_template('victim.html')

@app.route('/request', methods=['GET', 'POST'])
def request_page():

    if request.method == 'POST':

        try:

            request_id = request.form['request_id']
            victim_id = request.form['victim_id']
            priority = request.form['priority']
            status = request.form['status']

            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO Emergency_Request
                VALUES(:1,:2,:3,:4)
            """, (
                request_id,
                victim_id,
                priority,
                status
            ))

            connection.commit()

            return "Emergency Request Submitted Successfully"

        except Exception as e:

            return f"Database Error: {e}"

    return render_template('emergency_request.html')

@app.route('/dashboard')
def dashboard():

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM Victim")
    victims = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Emergency_Request WHERE Status='Pending'")
    requests = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(Quantity) FROM Resources")
    resources = cursor.fetchone()[0]

    return render_template(
        'dashboard.html',
        victims=victims,
        requests=requests,
        resources=resources
    )

@app.route('/alerts')
def alerts():

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Emergency_Request WHERE Priority='High'")

    alerts_data = cursor.fetchall()

    return render_template('alerts.html', alerts=alerts_data)

@app.route('/resources', methods=['GET', 'POST'])
def resources():

    resources_data = []
    searched = False

    if request.method == 'POST':

        location_id = request.form['location_id']
        searched = True

        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM Resources WHERE location_id = :loc_id",
                {"loc_id": location_id}
            )
            resources_data = cursor.fetchall()

        except Exception as e:
            print("DB Error:", e)
            resources_data = []

    return render_template('resource_finder.html', resources=resources_data, searched=searched)

@app.route('/manage_resources', methods=['GET', 'POST'])
def manage_resources():

    if request.method == 'POST':

        try:

            resource_id = request.form['resource_id']
            resource_name = request.form['resource_name']
            quantity = request.form['quantity']

            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO Resources
                VALUES(:1,:2,:3)
            """, (
                resource_id,
                resource_name,
                quantity
            ))

            connection.commit()

            return "Resource Added Successfully"

        except Exception as e:

            return f"Database Error: {e}"

    return render_template('resource_management.html')


@app.route('/analytics')
def analytics():

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM Emergency_Request WHERE Priority='High'")
    high = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Emergency_Request WHERE Priority='Medium'")
    medium = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Emergency_Request WHERE Priority='Low'")
    low = cursor.fetchone()[0]

    return render_template('analytics.html', high=high, medium=medium, low=low)
@app.route('/query', methods=['GET', 'POST'])
def query_runner():
    results = []
    columns = []
    error = None
    query = ''

    if request.method == 'POST':
        query = request.form['query']
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            if query.strip().upper().startswith('SELECT'):
                columns = [col[0] for col in cursor.description]
                results = cursor.fetchall()
            else:
                connection.commit()
                results = None  # non-SELECT succeeded
        except Exception as e:
            error = str(e)

    return render_template('query_runner.html', results=results, columns=columns, error=error, query=query)


if __name__ == '__main__':
    app.run(debug=True)