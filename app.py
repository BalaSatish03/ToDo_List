from flask import Flask, request,render_template,redirect,url_for,session,jsonify
from flask_mysqldb import MySQL
app=Flask(__name__)
app.secret_key = 'satish_03'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Bala@2002'
app.config['MYSQL_DB'] = 'authentication'
mysql=MySQL(app)
'''@app.route('/')
def index():
    return render_template('index.html')'''
@app.route('/signup')
def signup():
    return render_template('signup.html')
@app.route('/')
def login():
    return render_template('login.html')
@app.route('/home')
def home():
    
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Retrieve tasks for the logged-in user
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))
    tasks = cur.fetchall()
    print(tasks)
    tasks_list = []
    for task in tasks:
        task_dict = {
            'id': task[0],
            'user_id': task[1],
            'content': task[2],
            'completed':task[3]
        }
        tasks_list.append(task_dict)
    cur.close()
    return render_template('home.html', tasks=tasks_list)
   
    

@app.route('/loginpage',methods=['GET'])
def retrieve():
    if request.method=='GET':
        name = request.args.get('name')
        password= request.args.get('password')
        cur=mysql.connection.cursor()
        cur.execute("SELECT * FROM credentials WHERE name= %s AND password= %s",(name,password))
        result=cur.fetchall()
        print(result)
        mysql.connection.commit()
        cur.close()
        if result:
            session['user_id'] = result[0][0]
    
            return redirect(url_for('home'))
            
        else:
            return render_template('login.html', is_invalid=True)  
    return render_template('login.html' , is_invalid=False)  
@app.route('/submit',methods=['POST'])
def ingest():
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cur=mysql.connection.cursor()
        cur.execute("SELECT name,email FROM credentials WHERE name= %s AND email= %s",(name,email))
        result=cur.fetchone()
        if result:
            is_invalid=True
            return render_template('signup.html',is_invalid=True)
        else:
            cur.execute("INSERT INTO credentials(name,email,password) values(%s,%s,%s)",(name,email,password))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('login'))
@app.route('/add_task', methods=['POST'])
def add_task():
    if request.method == 'POST':
        task = request.form.get('my_task')  # Assuming you're using form data

        # Ensure user is logged in
        if 'user_id' not in session:
            return redirect(url_for('login'))  # Redirect user to login page if not logged in

        # Insert task for the logged-in user
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tasks (task, user_id) VALUES (%s, %s)", (task, user_id))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('home'))  # Redirect user to home page after adding task
@app.route('/delete_task/<int:taskId>', methods=['DELETE'])
def delete_task(taskId):
    if request.method == 'DELETE':
        if 'user_id' not in session:
            return redirect(url_for('login')) 
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM tasks WHERE task_id = %s", (taskId,))
        mysql.connection.commit()
        cur.close()
        return 'success'
@app.route('/toggle_task/<int:taskId>', methods=['PUT'])
def toggle_task(taskId):
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    cur = mysql.connection.cursor()
    cur.execute("UPDATE tasks SET completed = 1-completed WHERE task_id = %s", (taskId,))
    mysql.connection.commit()
    cur.close()
    return 'Updated'
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))
        

       
if __name__ == '__main__':
    app.run(debug=True)