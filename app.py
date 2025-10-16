import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models.db import init_db, database# Imports from my database file

app = Flask(__name__)
app.secret_key = 'mysecretkey#123&***'

def get_db_connection():
    #establishing connection to the database.
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row # It allows me to access tables columns by name
    return conn

#home page calling or rendering
@app.route('/')
def home():
    return render_template('index.html')

# signup form setting
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup route."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not password or not confirm_password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))

        conn = get_db_connection()
        try:
            # Checking if username already exists.
            existing_user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'warning')
                return redirect(url_for('signup'))

            # Hashing password
            hashed_password = generate_password_hash(password)

            #Inserting new user into the database if doesn't exists already.
            conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                         (username, hashed_password, 'user'))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            flash(f'Database error during signup: {e}', 'danger')
            conn.rollback()
        finally:
            conn.close()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    #User and Admin login route.
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            # Storing user info into the session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            if user['role'] == 'admin':
                flash(f'Welcome, Admin {username}!', 'success')
                return redirect(url_for('admindashboard')) 
            else:
                flash(f'Welcome, {username}!', 'success')
                return redirect(url_for('userdashboard')) 
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html') 


@app.route('/userdashboard')
def userdashboard():
    # In a real app, check if user is logged in
    if 'role' not in session or session['role'] != 'user':
        flash('You must be logged in to view this page.', 'danger')
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Check for an active booking for the current user
    active_booking = conn.execute('''
        SELECT rs.id, rs.parking_timestamp, ps.spot_number, pl.prime_location_name
        FROM reserved_spots rs
        JOIN parking_spots ps ON rs.spot_id = ps.id
        JOIN parking_lots pl ON ps.lot_id = pl.id
        WHERE rs.user_id = ? AND rs.leaving_timestamp IS NULL
    ''', (user_id,)).fetchone()

    lots = []
    # If there is no active booking, then fetch the list of available lots
    if not active_booking:
        lots = lots = conn.execute('''
    SELECT
        pl.id,
        pl.prime_location_name,
        pl.price_per_hour,
        pl.address,
        pl.pincode,
        pl.maximum_number_of_spots,
        COUNT(ps.id) as occupied_spots
    FROM
        parking_lots pl
    LEFT JOIN
        parking_spots ps ON pl.id = ps.lot_id AND ps.status = 'occupied'
    GROUP BY
        pl.id
    ORDER BY
        pl.prime_location_name
    ''').fetchall()
    
    conn.close()
    
    # Pass both active_booking and lots to the template
    # One of them will be None/empty, and the template's 'if' statement will handle it.
    return render_template('userdashboard.html', active_booking=active_booking, lots=lots)

@app.route('/api/mostusedlot')
def mostusedlot():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    with get_db_connection() as conn:
        # This query counts how many times the user has booked a spot in each lot
        data = conn.execute('''
            SELECT pl.prime_location_name, COUNT(rs.id) as booking_count
            FROM reserved_spots rs
            JOIN parking_spots ps ON rs.spot_id = ps.id
            JOIN parking_lots pl ON ps.lot_id = pl.id
            WHERE rs.user_id = ?
            GROUP BY pl.prime_location_name
        ''', (user_id,)).fetchall()
        
        # Format the data for the chart
        labels = [row['prime_location_name'] for row in data]
        values = [row['booking_count'] for row in data]
        
        return jsonify(labels=labels, values=values)
    
@app.route('/api/usermonthlycost')
def usermonthlycost():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    with get_db_connection() as conn:
        # This query sums up the total cost for each month
        data = conn.execute('''
            SELECT
                strftime('%Y-%m', leaving_timestamp) as month,
                SUM(total_cost) as total
            FROM
                reserved_spots
            WHERE
                user_id = ? AND leaving_timestamp IS NOT NULL
            GROUP BY
                month
            ORDER BY
                month
        ''', (user_id,)).fetchall()
        
        # Format the data for the chart
        labels = [row['month'] for row in data]
        values = [row['total'] for row in data]
        
        return jsonify(labels=labels, values=values)


@app.route('/bookspot/<int:lot_id>', methods=['POST'])
def bookspot(lot_id):
    #Ensuring the user is logged in
    if 'user_id' not in session:
        flash('You must be logged in to book a spot.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if the user already has an active booking
        active_booking = conn.execute(
            'SELECT id FROM reserved_spots WHERE user_id = ? AND leaving_timestamp IS NULL', (user_id,)
        ).fetchone()

        if active_booking:
            flash('You already have an active parking spot.', 'warning')
            return redirect(url_for('userdashboard'))

        # Find the first available spot in the selected lot
        available_spot = cursor.execute(
            'SELECT id FROM parking_spots WHERE lot_id = ? AND status = ? LIMIT 1', (lot_id, 'available')
        ).fetchone()

        if available_spot:
            spot_id = available_spot['id']
            
            # Get the price from the parking lot
            lot_price = conn.execute('SELECT price_per_hour FROM parking_lots WHERE id = ?', (lot_id,)).fetchone()['price_per_hour']

            # 1. Update the spot status to 'occupied'
            cursor.execute('UPDATE parking_spots SET status = ? WHERE id = ?', ('occupied', spot_id))

            # 2. Create a new reservation record
            cursor.execute(
                'INSERT INTO reserved_spots (spot_id, user_id, parking_timestamp, parking_cost_per_unit) VALUES (?, ?, ?, ?)',
                (spot_id, user_id, datetime.now().strftime('%Y-%m-%d %H:%M'), lot_price)
            )
            
            conn.commit()
            flash('Your spot has been successfully booked!', 'success')
        else:
            flash('Sorry, no spots are available in this lot at the moment.', 'danger')

    return redirect(url_for('userdashboard'))

@app.route('/vacatespot/<int:booking_id>', methods=['POST'])
def vacatespot(booking_id):
    if 'user_id' not in session:
        flash('You must be logged in to perform this action.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Find the active booking to ensure the user owns it
        booking = cursor.execute(
            'SELECT * FROM reserved_spots WHERE id = ? AND user_id = ? AND leaving_timestamp IS NULL',
            (booking_id, user_id)
        ).fetchone()

        if booking:
            spot_id = booking['spot_id']
            
            # --- Calculate Parking Cost ---
            start_time_str = booking['parking_timestamp']
            cost_per_hour = booking['parking_cost_per_unit']
            
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M')
            end_time = datetime.now()
            
            duration_hours = (end_time - start_time).total_seconds() / 3600
            total_cost = duration_hours * cost_per_hour
            
            # --- Update Database ---
            # 1. Mark the booking as complete with timestamps and cost
            cursor.execute(
                'UPDATE reserved_spots SET leaving_timestamp = ?, total_cost = ? WHERE id = ?',
                (end_time.strftime('%Y-%m-%d %H:%M'), total_cost, booking_id)
            )
            # 2. Mark the parking spot as available again
            cursor.execute('UPDATE parking_spots SET status = ? WHERE id = ?', ('available', spot_id))
            
            conn.commit()
            flash(f'Spot vacated successfully! Your total cost is ₹{total_cost:.2f}.', 'success')
        else:
            flash('Active booking not found or you do not have permission to vacate it.', 'danger')

    return redirect(url_for('userdashboard'))

@app.route('/userhistory')
def userhistory():
    if 'user_id' not in session:
        flash('You must be logged in to view your history.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    with get_db_connection() as conn:
        history = conn.execute('''
            SELECT rs.parking_timestamp, rs.leaving_timestamp, rs.total_cost, pl.prime_location_name, ps.spot_number
            FROM reserved_spots rs
            JOIN parking_spots ps ON rs.spot_id = ps.id
            JOIN parking_lots pl ON ps.lot_id = pl.id
            WHERE rs.user_id = ? AND rs.leaving_timestamp IS NOT NULL
            ORDER BY rs.parking_timestamp DESC
        ''', (user_id,)).fetchall()
    
    return render_template('userhistory.html', history=history)

@app.route('/user/usersummarychart')
def usersummarychart():
    return render_template('usersummarychart.html')

@app.route('/admindashboard')
def admindashboard():
    if 'role' not in session or session['role'] != 'admin':
        flash('You must be logged in as an admin to view this page.', 'danger')
        return redirect(url_for('login'))
    conn = get_db_connection()
    lots = lots = conn.execute('''
    SELECT
        pl.id,
        pl.prime_location_name,
        pl.price_per_hour,
        pl.address,
        pl.pincode,
        pl.maximum_number_of_spots,
        (SELECT COUNT(*) FROM parking_spots ps WHERE ps.lot_id = pl.id AND ps.status = 'occupied') as occupied_spots
        FROM parking_lots pl
        ORDER BY pl.prime_location_name
    ''').fetchall()
    occupiedspots_details = {}
    for lot in lots:
        details = conn.execute('''
            SELECT ps.spot_number, u.username, rs.parking_timestamp
            FROM reserved_spots rs
            JOIN parking_spots ps ON rs.spot_id = ps.id
            JOIN users u ON rs.user_id = u.id
            WHERE ps.lot_id = ? AND rs.leaving_timestamp IS NULL
            ORDER BY ps.spot_number
        ''', (lot['id'],)).fetchall()
        occupiedspots_details[lot['id']] = details
    conn.close()
    return render_template('admindashboard.html', lots=lots , occupiedspots_details=occupiedspots_details)

@app.route('/admin/adminsummarychart')
def adminsummarychart():
    return render_template('adminsummarychart.html')

@app.route('/api/admin/peakhours')
def peakhours():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Not authorized'}), 403

    with get_db_connection() as conn:
        # This query counts bookings started per hour for the current day
        data = conn.execute('''
            SELECT
                strftime('%H', parking_timestamp) as hour,
                COUNT(id) as booking_count
            FROM
                reserved_spots
            WHERE
                date(parking_timestamp) = date('now', 'localtime')
            GROUP BY
                hour
            ORDER BY
                hour
        ''').fetchall()

        # Prepare a full 24-hour dataset
        labels = [f"{h:02d}:00" for h in range(24)]
        values = [0] * 24
        for row in data:
            hour_index = int(row['hour'])
            values[hour_index] = row['booking_count']
        
        return jsonify(labels=labels, values=values)
    
@app.route('/api/admin/lotoccupancy')
def lotoccupancy():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Not authorized'}), 403

    with get_db_connection() as conn:
        # This is the same query from your dashboard table
        data = conn.execute('''
            SELECT pl.prime_location_name, COUNT(ps.id) as occupied_count
            FROM parking_lots pl
            LEFT JOIN parking_spots ps ON pl.id = ps.lot_id AND ps.status = 'occupied'
            GROUP BY pl.id
            ORDER BY occupied_count DESC
        ''').fetchall()

        labels = [row['prime_location_name'] for row in data]
        values = [row['occupied_count'] for row in data]

        return jsonify(labels=labels, values=values)
    
@app.route('/admin/allusers')
def allusers():
    if 'role' not in session or session['role'] != 'admin':
        flash('You must be an admin to view this page.', 'danger')
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        users = conn.execute("SELECT id, username, role FROM users WHERE role = 'user' ORDER BY username").fetchall()
    
    return render_template('allusers.html', users=users)

@app.route('/admin/createlot', methods=['GET', 'POST'])
def createlot():
    # Protecting the route
    if 'role' not in session or session['role'] != 'admin':
        flash('You must be an admin to perform this action.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Getting the data from the form
        name = request.form['prime_location_name']
        price = request.form['price_per_hour']
        spots = request.form['maximum_number_of_spots']
        address = request.form.get('address', '') # .get is safer for optional fields
        pincode = request.form.get('pincode', '')

        if not name or not price or not spots:
            flash('Name, Price, and Number of Spots are required!', 'danger')
            return redirect(url_for('createlot'))

        conn = get_db_connection()
        try:
            # 3. Inserting the new parking lot
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO parking_lots (prime_location_name, price_per_hour, maximum_number_of_spots, address, pincode) VALUES (?, ?, ?, ?, ?)',
                (name, float(price), int(spots), address, pincode)
            )
            # Get the ID of the lot we just created
            lot_id = cursor.lastrowid

            # 4. Automatically create the parking spots for this lot
            for spot_num in range(1, int(spots) + 1):
                cursor.execute(
                    'INSERT INTO parking_spots (lot_id, spot_number, status) VALUES (?, ?, ?)',
                    (lot_id, spot_num, 'available')
                )
            
            # 5. Commit all changes
            conn.commit()
            flash(f'Parking lot "{name}" and its {spots} spots have been created successfully!', 'success')
            return redirect(url_for('admindashboard'))

        except sqlite3.IntegrityError:
            flash(f'A parking lot with the name "{name}" already exists.', 'warning')
            conn.rollback()
        except sqlite3.Error as e:
            flash(f'Database error: {e}', 'danger')
            conn.rollback()
        finally:
            conn.close()

    # For a GET request, you would normally show a form.
    # Since we are creating dummy pages, we'll just return a simple message.
    return render_template('createlot.html')

@app.route('/admin/deletelot/<int:lot_id>', methods=['POST'])
def deletelot(lot_id):
    if 'role' not in session or session['role'] != 'admin':
        flash('You must be an admin to perform this action.', 'danger')
        return redirect(url_for('login'))
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if any spots in the lot are occupied
        occupied_count = cursor.execute(
            'SELECT COUNT(id) FROM parking_spots WHERE lot_id = ? AND status = ?', (lot_id, 'occupied')
        ).fetchone()[0]

        if occupied_count > 0:
            flash('Cannot delete a lot that has parked vehicles.', 'danger')
        else:
            # ON DELETE CASCADE in the database will handle deleting the spots
            cursor.execute('DELETE FROM parking_lots WHERE id = ?', (lot_id,))
            conn.commit()
            flash('Parking lot deleted successfully.', 'success')
            
    return redirect(url_for('admindashboard'))

@app.route('/admin/editlot/<int:lot_id>', methods=['GET', 'POST'])
def editlot(lot_id):
    if 'role' not in session or session['role'] != 'admin':
        flash('You must be an admin to perform this action.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form['prime_location_name']
        price = request.form['price_per_hour']
        address = request.form['address']
        pincode = request.form['pincode']
        
        conn.execute(
            'UPDATE parking_lots SET prime_location_name = ?, price_per_hour = ?, address = ?, pincode = ? WHERE id = ?',
            (name, price, address, pincode, lot_id)
        )
        conn.commit()
        conn.close()
        flash('Parking lot details updated successfully.', 'success')
        return redirect(url_for('admindashboard'))

    # For a GET request, fetch the lot data and show the form
    lot = conn.execute('SELECT * FROM parking_lots WHERE id = ?', (lot_id,)).fetchone()
    conn.close()
    if lot is None:
        flash('Lot not found.', 'danger')
        return redirect(url_for('admindashboard'))
        
    return render_template('editlot.html', lot=lot)



@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

