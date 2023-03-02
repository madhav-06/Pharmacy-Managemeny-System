from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors


app=Flask(__name__)

#configuration of db
app.config['MYSQL_HOST']="127.0.0.1"
app.config['MYSQL_USER']="root"
app.config['MYSQL_PASSWORD']="Bindu@143"
app.config['MYSQL_DB']="flaskapp"

mysql=MySQL(app)

admin_name=""
bill_number=10000

@app.route('/')
@app.route('/login',methods=["GET","POST"])
def login():
    msg=""
    if request.method=="POST":
        logindetails=request.form
        cur=mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        query="select * from admin_details where email='"+logindetails['email']+"' and pass='"+logindetails['password']+"'"
        cur.execute(query)
        

        # email=logindetails['email']
        # password=logindetails['password']
        # cur.execute('SELECT * FROM admin_details WHERE email=%s AND pass=%s',(email,password,))


        #print(type(logindetails['email']))
        account=cur.fetchone()
        cur.close()
        # if account:
        #     msg='Logged in succesfully'
        #     return redirect(url_for('mainpage'))
        # else:
        #     msg='Incorrect username or password'
        cur.close()
        if account:
            global admin_name
            # msg="Welcome "+account['a_name']
            # admin_name=account['a_name']
            msg="Succesful Login"
            return render_template('mainpage.html',msg=msg)
            #return redirect(url_for('mainpage'))
        else:
            msg="Invalid credentials"

    return render_template('index.html',msg=msg)
    

@app.route('/signup',methods=["GET","POST"])
def signup():
    if request.method=="POST":
        userDetails=request.form
        name=userDetails['name']
        email=userDetails['email']
        password=userDetails['password']
        age=userDetails['age']
        city=userDetails['city']
        
        cur=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("INSERT INTO admin_details (a_name,email,pass,age,city) VALUES (%s,%s,%s,%s,%s)",(name,email,password,age,city))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/mainpage',methods=["GET","POST"])
def mainpage():
    if request.method=="POST":
        t_details=request.form
        name=t_details['name']
        cur=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM stock_details WHERE t_name=%s',(name,))
        tablet=cur.fetchone()
        cur.close()
        #print(tablet, name)
        if tablet:
            #return render_template('tablet_details.html',tdetails=tablet)
            return redirect(url_for('tablet_details',name=name))


    return render_template('mainpage.html',msg="Welcome "+admin_name)


@app.route('/tablet_details',methods=["GET","POST"])
def tablet_details():
    tablet_name=request.args.get('name')
    cur=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM stock_details WHERE t_name=%s',(tablet_name,))
    tablet_detail=cur.fetchone()
    cur.close()
    if request.method=="POST":
        quantity=request.form
        #name=tablet_name
        name=quantity['name']
        quantity=int(quantity['quantity'])
        
        cur=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM cart WHERE t_name=%s',(name,))
        tab=cur.fetchone()
        if tab:
            quantity1=int(tab['quantity'])
            quantity+=quantity1
            quantity=str(quantity)
            cur.execute("UPDATE cart SET quantity=%s WHERE t_name=%s",(quantity,name))
            mysql.connection.commit()
            cur.close()
        else:
            cur.execute("SELECT pid FROM stock_details WHERE stock_details.t_name=%s",(name,))
            pid=cur.fetchone()['pid']
            #pid=str(pid)
            cur.execute("INSERT INTO cart VALUES (%s,%s,%s)",(pid,name,quantity,))
            mysql.connection.commit()
            cur.close()

        return render_template('mainpage.html',msg="Welcome "+admin_name)

    return render_template('tablet_details.html',tdetails=tablet_detail)


@app.route('/cart')
def cart():
    cur=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM cart')
    details=cur.fetchall()
    cur.close()


    return render_template('cart.html',details=details)


@app.route('/invoice')
def invoice():
    global bill_number
    print(bill_number)
    cur=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM cart")
    details=cur.fetchall()
    #print(details[0])
    for i in details:
        pid=i['pid']
        t_name=i['t_name']
        quantity=i['quantity']
        cur.execute("SELECT price FROM stock_details, cart WHERE stock_details.pid=%s and cart.pid=%s",(pid,pid,))
        price=cur.fetchone()['price']
        cost=price*quantity
        cur.execute("INSERT INTO invoice values (%s,%s,%s,%s,%s,%s,%s)",(bill_number,pid,t_name,price,quantity,'2022-12-03',cost))
        mysql.connection.commit()

    cur.execute("SELECT * FROM invoice WHERE bill_no=%s",(bill_number,))
    invoice_details=cur.fetchall()
    cur.execute("SELECT sum(cost) as total FROM invoice WHERE bill_no=%s",(bill_number,))
    total=cur.fetchone()['total']

    cur.execute("TRUNCATE TABLE cart")
    bill_number+=1
    #print(bill_number)
    mysql.connection.commit()

    cur.close()
    return render_template('invoice.html',invoice_details=invoice_details,total=total)
    #return details


if __name__=="__main__":
    app.run(debug=True)