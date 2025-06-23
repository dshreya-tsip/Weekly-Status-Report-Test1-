from flask import Flask, request, jsonify, render_template, send_file
import psycopg2
import os
import io
import csv

app = Flask(__name__)
DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data', methods=['GET'])
def load_data():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT year, month, weekdays, etria, solutions FROM weekly_status")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save', methods=['POST'])
def save_data():
    data = request.json.get('tableData')
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM weekly_status")
        for row in data:
            cur.execute(
                "INSERT INTO weekly_status (year, month, weekdays, etria, solutions) VALUES (%s, %s, %s, %s, %s)",
                row
            )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Data saved successfully to PostgreSQL'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_csv')
def download_csv():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT year, month, weekdays, etria, solutions FROM weekly_status")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Year", "Month", "Week Days", "Etria", "Solutions"])
        writer.writerows(rows)

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype="text/csv",
            download_name="WeeklyStatusReport.csv",
            as_attachment=True
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)