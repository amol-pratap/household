#App routes
from flask import Flask,render_template,request,url_for,redirect
from flask import current_app as app
from .models import *
from datetime import date,datetime
from flask_migrate import Migrate
from sqlalchemy import func
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sqlalchemy import or_
from werkzeug.utils import secure_filename
import os




@app.route("/")
def Home():
    return render_template("index.html")

 
@app.route("/login",methods=["GET","POST"])
def signin():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        
        #admin dashboard
        if uname=="admin@gmail.com" and pwd=="adminpassword":
            return redirect(url_for("admin_dashboard",name=uname))
        
        #professional dashboard  
        usr=Professional.query.filter_by(email=uname,password=pwd).first()
        if usr:    #if user exists
            return redirect(url_for("professional_dashboard",name=uname)) 
      
        #customer dashboard
        usr=Customer.query.filter_by(email=uname,password=pwd).first()
        if usr:    #if user exists
            return redirect(url_for("customer_dashboard",name=uname))
        else: 
            return render_template("login.html",msg="Inavalid user and credetials")
        
    return render_template("login.html",msg="")


@app.route("/register_professional",methods=["GET","POST"])
def register_professional():
    if request.method=="POST":
        uname=request.form.get("user_name")
        if uname =="":
            return render_template("professional_signup.html",msg="you not entered email, please enter Email")
        else:
            ex_usr=Professional.query.filter_by(email=uname).first()
            if ex_usr:
                return render_template("professional_signup.html",msg="User already exists, please login")
        full_name=request.form.get("full_name")
        Service_type=request.form.get("service_type")
        experience=request.form.get("experience")
        address=request.form.get("address")
        pin_code=request.form.get("pin_code")
        mobile_number=request.form.get("mob_num")
        description=request.form.get("description")
        pwd=request.form.get("password")
        current_date = date.today()
        formatted_date = current_date.strftime("%d-%m-%Y")
        
        file=request.files["file_upload"]
        url=""
        if file.filename:
            file_name=secure_filename(file.filename) #Verification of the file is done
            upload_folder = './static/uploaded_cv/'
            #url=upload_folder+uname+"_"+file_name
            url=os.path.join(upload_folder, file_name)
            file.save(url)
        
        # Creating a new Professional object with the form data
        new_usr=Professional(email=uname,full_name=full_name,service_type=Service_type,experience=experience,address=address,pincode=pin_code,mobile_number=mobile_number,date_created=formatted_date,description=description,password=pwd,cv=os.path.basename(url))
        # Add to the session and commit to save in database
        db.session.add(new_usr)
        db.session.commit()
        return render_template("login.html",msg="Registration Successfull, login now")
    
    return render_template("professional_signup.html",Services=get_services(),msg="")


@app.route("/register_customer",methods=["GET","POST"])
def register_customer():
    if request.method=="POST":
        uname=request.form.get("user_name")
        if uname =="":
            return render_template("customer_signup.html",msg="you not entered email, please enter Email")
        else:
            ex_usr=Customer.query.filter_by(email=uname).first()
            if ex_usr:
                return render_template("customer_signup.html",msg="User already exists, please login")
        full_name=request.form.get("full_name")
        address=request.form.get("address")
        pin_code=request.form.get("pin_code")
        mobile_number=request.form.get("mob_num")
        current_date = date.today()
        formatted_date = current_date.strftime("%d-%m-%Y")
        description=request.form.get("description")
        pwd=request.form.get("password")
        
        # Creating a new Professional object with the form data
        new_usr=Customer(email=uname,full_name=full_name,address=address,pincode=pin_code,mobile_number=mobile_number,date_created=formatted_date,description=description,password=pwd)
        # Add to the session and commit to save in database
        db.session.add(new_usr)
        db.session.commit()
        return render_template("login.html",msg="Registration Successfull, login now")
        
    return render_template("customer_signup.html",msg="")


#common route for admin dashboard
@app.route("/admin/<name>")
def admin_dashboard(name):
    services=get_services()
    professionals=get_professionals()
    services_request=get_services_request_admin()
    return render_template("admin_dashboard.html",name=name,services=services,professionals=professionals,services_request=services_request)

#common route for professional dashboard
@app.route("/professional/<name>")
def professional_dashboard(name):
    services_request=all_services_request(name)
    services_request=get_customer_service_history_to_professional(name)
    return render_template("professional_dashboard.html",name=name,services_request=services_request)

#common route for customer dashboard
@app.route("/customer/<name>")
def customer_dashboard(name):
    services=get_services()
    customer=get_customer(name)
    services_request=get_customer_service_history(name)
    return render_template("customer_dashboard.html",name=name,services=services,customer=customer,services_request=services_request)   #services_request is specially created for access service request on customer dashboard

#common route for view service
@app.route("/view_services/<service_professional>/<service>/<cid>/<name>")
def view_services(service_professional,service,cid,name):
    cnf_msg=" Congratulations, Service Booked Successfully! Do you Want any other Service"
    return render_template("view_service.html",service_professional=service_professional,service=service,cid=cid,name=name) 




#many controller/routers
@app.route("/add_service/<name>",methods=["GET","POST"])
def add_service(name):
    if request.method=="POST":
        service_name=request.form.get("service_name")
        price=request.form.get("price")
        #time_required=request.form.get("time_required")
        description=request.form.get("description")
        
        # Creating a new Service object with the form data
        new_service=Service(name=service_name,price=price,description=description)
        # Add to the session and commit to save in database
        db.session.add(new_service)
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
           
    return render_template("add_service.html",name=name)


@app.route("/search_admin/<name>",methods=["GET","POST"])
def search_admin(name):
    if request.method=="POST":
        search_txt=request.form.get("search_txt")
        category=request.form.get("category")       # Drop-down t0 select a category
        result=""
        
        if category=="service":
            result=search_by_service(search_txt)
        elif category=="professional":
            result=search_by_professional(search_txt)
        elif category=="customer":
            result=search_by_customer(search_txt)
        elif category=="service_request":
            result=search_by_service_request(search_txt)
        return render_template("admin_search_view.html",name=name,category=category,results=result,msg="Not Found")
        
     
    return redirect(url_for("admin_dashboard",name=name))


@app.route("/search_professional/<name>",methods=["GET","POST"])
def search_professional(name):
    if request.method=="POST":
        professional=Professional.query.filter_by(email=name).first()
        search_txt=request.form.get("search_txt")
        category=request.form.get("category")       # Drop-down to select a category
        #result=""
        
        if category=="cust_name":
            result=Service_Request.query.join(Customer).filter(Service_Request.Professional_id==professional.id,Customer.full_name.ilike(f"%{search_txt}%")).all()
 
        elif category=="address":
            result=Service_Request.query.join(Customer).filter(Service_Request.Professional_id==professional.id,Customer.address.ilike(f"%{search_txt}%")).all()
        elif category=="service_date":
            result=Service_Request.query.filter(Service_Request.Professional_id==professional.id,Service_Request.service_date.ilike(f"%{search_txt}%")).all()
        return render_template("professional_search_view.html",name=name,category=category,results=result,msg="Not Found")
        
    return redirect(url_for("professional_dashboard",name=name)) 

@app.route("/search_customer/<name>",methods=["GET","POST"])
def search_customer(name):
    if request.method=="POST":
        customer=Customer.query.filter_by(email=name).first()
        search_txt=request.form.get("search_txt")
        category=request.form.get("category")       # Drop-down to select a category
        #result=""
        
        if category=="s_name":
            result=db.session.query(Professional, Service) \
                .join(Service, Service.name == Professional.service_type) \
                .filter(Service.name.ilike(f"%{search_txt}%")).all()
 
        elif category=="address":
            result=db.session.query(Professional, Service) \
                .join(Service, Service.name == Professional.service_type) \
                .filter(Professional.address.ilike(f"%{search_txt}%")).all()
        elif category=="pin_code":
            if search_txt.isdigit():
                result=db.session.query(Professional, Service) \
                    .join(Service, Service.name == Professional.service_type) \
                    .filter(Professional.pincode==int(search_txt)).all()
            else:
                result = "" 
        else:
            return render_template("customer_search_view.html",name=name,msg="Not Found")
            
        return render_template("customer_search_view.html",name=name,cid=customer.id,results=result,msg="Not Found")
        
    return redirect(url_for("customer_dashboard",name=name))     

#Profile
@app.route("/professional_profile/<name>",methods=["GET","POST"])
def professional_profile(name):
    professional=get_professional(name)
    return render_template("professional_profile.html",name=name,professional=professional)

@app.route("/customer_profile/<name>",methods=["GET","POST"])
def customer_profile(name):
    customer=get_customer(name)
    return render_template("customer_profile.html",name=name,customer=customer)

@app.route("/view_professional_profile/<p_name>/<name>",methods=["GET","POST"])
def view_professional_profile(p_name,name):
    professional = Professional.query.filter_by(email=p_name).first()

    service_requests = Service_Request.query.filter_by(Professional_id=professional.id).all()
    reviews = []
    for request in service_requests:
        review = {
        'rating': request.rating,
        'review': request.review,
        'customer_name': request.customer.full_name
            }
        reviews.append(review)
        
    return render_template("view_professional_profile.html",name=name,professional=professional,reviews=reviews)
            
            
            

@app.route("/edit_service/<sid>/<name>",methods=["GET","POST"])
def edit_service(sid,name):
    service=get_service(sid)
    if request.method=="POST":
        #taking  data from form
        service_name=request.form.get("service_name")
        price=request.form.get("price")
        description=request.form.get("description")
        #updating data
        service.name=service_name
        service.price=price
        service.description=description
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
    
    return render_template("edit_service.html",name=name,service=service)
        

@app.route("/delete_service/<id>/<name>",methods=["GET","POST"])
def delete_service(id,name):
    service=get_service(id)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for("admin_dashboard",name=name))

@app.route("/delete_professional/<pid>/<name>")
def delete_professional(pid,name):
    professional = Professional.query.filter_by(id=pid).first()
    db.session.delete(professional)
    db.session.commit()
    return redirect(url_for("admin_dashboard",name=name))


@app.route("/view_service/<sid>/<cid>/<name>",methods=["GET","POST"])
def view_service(sid,cid,name):
    service=get_service(sid)
    service_type=service.name
    Service_professional=get_all_professionals(service_type)
    
    return render_template("view_service.html",service_professional=Service_professional,service=service,name=name,cid=cid)

@app.route("/book_service/<sid>/<cid>/<pid>/<name>",methods=["GET","POST"])
def book_service(sid,cid,pid,name):
    professional=get_professional_by_id(pid)   #Professional.query.filter_by(id=pid).first()
    service=get_service(sid) 
    if request.method=="POST":
        #taking  data from form
        current_date = date.today()
        current_date = current_date.strftime("%d-%m-%Y")
        service_date=request.form.get("service_date")
        service_date=datetime.strptime(service_date, "%Y-%m-%d")
        service_date = service_date.strftime("%d-%m-%Y")
        description=request.form.get("description")
        status="Requested"
        new_service_request=Service_Request(Service_id=sid,Customer_id=cid,Professional_id=pid,date_of_request=current_date,service_date=service_date,description=description,status=status)
        db.session.add(new_service_request)
        db.session.commit()
        
        service=get_service(sid)
        return redirect(url_for("customer_dashboard",name=name))
        
       
    
    return render_template("book_service.html",professional=professional,service=service,name=name,cid=cid)
     

@app.route("/edit_request/<sr_id>/<name>",methods=["GET","POST"])   #when customer want to edit request
def edit_service_request(sr_id,name):
    #professional=Professional.query.filter_by(id=pid).first()
    #service=get_service(sid)
    services_request=get_customer_service_history(name)
    edit_request_data=next((item for item in services_request if item.request_id==int(sr_id)),None)

    if request.method=="POST":
        service_request=get_one_service_request(sr_id)
        #taking  data from form
        description=request.form.get("description")
        date=request.form.get("service_date")
        date=datetime.strptime(date, "%Y-%m-%d")
        date = date.strftime("%d-%m-%Y")
        #updating data
        service_request.description=description
        service_request.service_date=date
        db.session.commit()
        return redirect(url_for("customer_dashboard",name=name))
    
    return render_template("edit_request.html",name=name,sr_id=sr_id,edit_request_data=edit_request_data)
    return render_template("edit_reuest.html",professional=professional,service=service,name=name,cid=cid,sr_id=sr_id)
    
@app.route("/close_request/<sr_id>/<name>",methods=["GET","POST"])   #when customer want to close request after service done
def close_service_request(sr_id,name):
    service_request=get_one_service_request(sr_id)
    pid=service_request.Professional_id
    professional=get_professional_by_id(pid)
    if request.method == "POST":
        review = request.form.get("review")
        rating = int(request.form.get("rating"))
        #update
        service_request.review=review
        service_request.rating=rating
        service_request.status="closed"
        #update Professional profile
        rating_sum=float(professional.rating) * int(professional.rating_count)
        professional.rating_count =int(professional.rating_count)+1
        rating_now=(float(rating_sum)+service_request.rating)/professional.rating_count
        professional.rating=f"{rating_now:.2f}"
        current_date = date.today()
        current_date = current_date.strftime("%d-%m-%Y")
        service_request.date_of_completion=current_date
        db.session.commit()
        return redirect(url_for("customer_dashboard",name=name))
    
    return render_template("review_service.html",name=name,sr_id=sr_id)




    
@app.route("/update_service_request/<sr_id>/<name>",methods=["GET","POST"])    #when Professional will accept a service request
def update_service_request(sr_id,name):
    request=get_one_service_request(sr_id)
    request.status="Accepted, Ongoing"
    db.session.commit()
    return redirect(url_for("professional_dashboard",name=name)) 

@app.route("/reject_service_request/<sr_id>/<name>",methods=["GET","POST"])   #when Professional will reject a service request
def reject_service_request(sr_id,name):
    request=get_one_service_request(sr_id)
    request.status="Rejected"
    db.session.commit()
    return redirect(url_for("professional_dashboard",name=name))
   

#SUMMARY
@app.route("/admin_summary/<name>")
def admin_summary(name):
    plot=get_admin_summary()
    plot.savefig(f"./static/image/{name}_admin_summary.jpeg")
    plot.clf()
    return render_template("admin_summary.html",name=name)

@app.route("/professional_summary/<name>")
def professional_summary(name):
    plot=get_professional_summary(name)
    plot.savefig(f"./static/image/professional/{name}_professional_summary.jpeg")
    plot.clf()
    return render_template("professional_summary.html",name=name)

@app.route("/customer_summary/<name>")
def customer_summary(name):
    plot=get_customer_summary(name)
    plot.savefig(f"./static/image/customer/{name}_customer_summary.jpeg")
    plot.clf()
    return render_template("customer_summary.html",name=name)


   
   
   
   
#other supported function
#Service function
def get_services():
    services = Service.query.all()  
    return services

def get_service(sid):
    service = Service.query.filter_by(id=sid).first() 
    return service

#Professional function
def get_professionals():
    professionals = Professional.query.order_by(Professional.rating.desc()).limit(5).all()  
    return professionals

def get_all_professionals(service_type):
    professionals = Professional.query.filter_by(service_type=service_type).all()
    return professionals

def get_professional(name):
    professional=Professional.query.filter_by(email=name).first()
    return professional

def get_professional_by_id(pid):
    Professionals=Professional.query.filter_by(id=pid).first()
    return Professionals

def get_customer_service_history_to_professional(name):
    professional=get_professional(name)
    professional_id=professional.id
    service_history = (
        db.session.query(
            Service_Request.id.label("request_id"),
            Customer.full_name.label("customer_name"),
            Customer.mobile_number.label("customer_mobile"),
            Customer.address.label("customer_address"),
            Service_Request.service_date.label("service_date"),
            Service_Request.status.label("service_status"),
            Service_Request.rating.label("service_rating")
        )
        .join(Service, Service_Request.Service_id == Service.id)
        .join(Customer, Service_Request.Customer_id == Customer.id)
        .filter(Service_Request.Professional_id == professional.id)
        .all()
    )
    return service_history



#Customers function
def get_customer(name):
    customer=Customer.query.filter_by(email=name).first()
    return customer



def get_customer_service_history(name):
    customer=get_customer(name)
    customer_id=customer.id
    service_history = (
        db.session.query(
            Service_Request.id.label("request_id"),
            Service.name.label("service_name"),
            Service.price.label("service_price"),
            Professional.full_name.label("professional_name"),
            Professional.address.label("professional_address"),
            Professional.mobile_number.label("professional_mobile"),
            Professional.description.label("professional_description"),
            Service_Request.service_date.label("service_date"),
            Service_Request.status.label("status"),
            Service_Request.description.label("customer_description")
        )
        .join(Service, Service_Request.Service_id == Service.id)
        .join(Professional, Service_Request.Professional_id == Professional.id)
        .filter(Service_Request.Customer_id == customer.id)
        .all()
    )
    return service_history


#Service Request function
def get_services_request_admin():       #Service Request to admin
    #all_service_request = Service_Request.query.all()  
    all_service_request = Service_Request.query.order_by(Service_Request.id.desc()).limit(5).all() 
    return all_service_request

def get_all_services_request_admin():       #Service Request to admin
    #all_service_request = Service_Request.query.all()  
    all_service_request = Service_Request.query.order_by(Service_Request.id.desc()).all() 
    return all_service_request

def all_services_request(name):   #Service Request to Professional
    professional=get_professional(name)
    pid=professional.id
    all_service_request=Service_Request.query.filter_by(Professional_id=pid).all()
    return all_service_request

def get_services_request(name):       #Service Request to customer services_request
    customer=get_customer(name)
    cid=customer.id
    all_service_request=Service_Request.query.filter_by(Customer_id=cid).all()
    return all_service_request


        
def get_one_service_request(sr_id):
    service_request = Service_Request.query.filter_by(id=sr_id).first()
    return service_request
   
   
#Search Function 
def search_by_service(search_txt):
    services = Service.query.filter(or_(Service.name.ilike('%' + search_txt + '%'), Service.price.ilike('%' + search_txt + '%'))).all()
    return services


def search_by_professional(search_txt):
    professionals = Professional.query.filter(or_(Professional.full_name.ilike('%' + search_txt + '%'),Professional.service_type.ilike('%' + search_txt + '%'),Professional.experience.ilike('%' + search_txt + '%'))).order_by(Professional.rating.desc()).all()
    return professionals


def search_by_customer(search_txt):
    customers = Customer.query.filter(or_(Customer.full_name.ilike('%' + search_txt + '%'),Customer.address.ilike('%' + search_txt + '%'),Customer.date_created.ilike('%' + search_txt + '%'))).all()
    return customers

def search_by_service_request(search_txt):
    service_requests = Service_Request.query.filter(or_(Service_Request.status.ilike('%' + search_txt + '%'),Service_Request.service_date.ilike('%' + search_txt + '%'),Service_Request.id.ilike('%' + search_txt + '%'))).all()
    return service_requests  


def get_service(id):
    service = Service.query.filter_by(id=id).first()
    return service


#Summary Function
def get_admin_summary():
    req=get_all_services_request_admin()
    summary={}
    for r in req:
        if r.status not in summary:
            summary[r.status]=0
        summary[r.status]+=1
    x_status=list(summary.keys())
    y_number= list(summary.values())
    plt.bar(x_status,y_number,color="blue",width=0.5)
    plt.title("Service Request Status summary")
    plt.xlabel("status")
    plt.ylabel("number of requests")
    return plt

def get_professional_summary(name):
    req=all_services_request(name)   #all request to a particular professional
    summary={}
    for r in req:
        if r.status not in summary:
            summary[r.status]=0
        summary[r.status]+=1
    x_status=list(summary.keys())
    y_number= list(summary.values())
    plt.bar(x_status,y_number,color="blue",width=0.5)
    plt.title("Service Request Status summary")
    plt.xlabel("status")
    plt.ylabel("number of requests")
    return plt

 
              
def get_customer_summary(name):
    req=get_services_request(name)   #all request by a particular customer
    summary={}
    for r in req:
        if r.status not in summary:
            summary[r.status]=0
        summary[r.status]+=1
    x_status=list(summary.keys())
    y_number= list(summary.values())
    plt.bar(x_status,y_number,color="blue",width=0.5)
    plt.title("Service Request Status summary")
    plt.xlabel("status")
    plt.ylabel("number of requests")
    return plt                                                            