from flask import Flask,render_template,redirect,request
from flask import current_app as app
from .models import *
from .utils import *
import matplotlib.pyplot as plt
import os


@app.route("/")
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    else:
        username=request.form.get("user_name")
        password=request.form.get("pwd")

        this_user=User.query.filter_by(username=username).first()
        if this_user:
            if this_user.password==password:
                if this_user.type=="admin":
                    return redirect("/admin_dash")
                else:
                    return redirect(f"/user_dash/{this_user.id}")
            else:
                return render_template("incorect_p.html")
        else:
            return render_template("not_exist.html")


@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="GET":
        return render_template("register.html")
    else:
        username=request.form.get("user_name")
        password=request.form.get("pwd")
        email=request.form.get("email")

        user_email=User.query.filter_by(email=email).first()
        user_id=User.query.filter_by(username=username).first()

        if user_id or user_email:
            return render_template("already.html")
        else:
            new_user=User(username=username,email=email,password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")

     
@app.route("/admin_dash",methods=["GET","POST"])
def admin():
    this_user=User.query.filter_by(type="admin").first()
    all_prod=Product.query.all()
    return render_template("admin_dash.html",this_user=this_user,all_prod=all_prod)


@app.route("/user_dash/<int:user_id>",methods=["GET","POST"])
def user(user_id):
    this_user=User.query.filter_by(id=user_id).first()
    all_prod=Product.query.all()
    return render_template("user_dash.html",this_user=this_user,all_prod=all_prod)


@app.route("/create_pod",methods=["GET","POST"])
def create_pod():
    if request.method=="GET":
        return render_template("create_pod.html")
    else:
        pod_name=request.form.get("pod_name")
        pod_cat=request.form.get("cat")
        pod_qunt=request.form.get("qunt")
        pod_cost=request.form.get("cost")

        new_pod=Product(prod_name=pod_name,category=pod_cat,quantity=pod_qunt,price=pod_cost)
        db.session.add(new_pod)
        db.session.commit()
        return redirect("/admin_dash")
    
@app.route("/update_prod/<int:prod_id>",methods=["GET","POST"])
def update_prod(prod_id):
    if request.method=="GET":
        prod=Product.query.filter_by(id=prod_id).first()
        return render_template("update_prod.html",prod=prod)
    else:
        prod_cat=request.form.get("cat")
        prod_qunt=request.form.get("qunt")
        prod_cost=request.form.get("cost")

        prod=Product.query.filter_by(id=prod_id).first()

        prod.catogery=prod_cat
        prod.quantity=prod_qunt
        prod.price=prod_cost

        db.session.commit()
        return redirect("/admin_dash")
    
@app.route("/admin/request")
def admin_requ():
    this_user=User.query.filter_by(type="admin").first()
    all_req=Request.query.all()
    return render_template("admin_req.html",this_user=this_user,all_req=all_req)
    
  

@app.route("/user/request/<int:user_id>", methods=["GET"] )
def request_page(user_id):
    this_user=User.query.filter_by(id=user_id).first()
    all_req=Request.query.filter_by(user_id=user_id).all()
    total=grand_total(all_req)
    return render_template("request.html",this_user=this_user,all_req=all_req, total=total)    

@app.route("/user_req/<int:prod_id>/<int:user_id>", methods=["GET","POST"])
def user_req(prod_id,user_id):
    if request.method=="GET":
        prod=Product.query.filter_by(id=prod_id).first()
        return render_template("user_req.html",prod=prod,user_id=user_id)
    else:
        prod_unit=request.form.get("qunt")

        new_request=Request(user_id=user_id,prod_id=prod_id,units_requested=prod_unit)
        db.session.add(new_request)
        db.session.commit() 
        return redirect(f"/user/request/{user_id}") 
    

@app.route("/approve/<int:req_id>")
def approve(req_id):
    req=Request.query.filter_by(id=req_id).first()
    prod=Product.query.filter_by(id=req.prod_id).first()
    if prod.quantity < req.units_requested:
        return "<h1> Insufficient Quantity </h1>"
    else:
        req.status="approved"
        prod.quantity = prod.quantity - req.units_requested
        db.session.commit()
    return redirect(f"/admin/request")

@app.route("/deny/<int:req_id>")
def deny(req_id):
    req=Request.query.filter_by(id=req_id).first()
    req.status="denied"
    db.session.commit()
    return redirect(f"/admin/request")


@app.route("/search")
def search():
    search_word = request.args.get("search")
    key = request.args.get("key")

    result=None
    requests = None

    if key == "user":
        result = User.query.filter_by(username=search_word).first()
        requests = Request.query.filter_by(user_id=result.id).all()

    elif key == "product":
        result = Product.query.filter_by(prod_name=search_word).first()
        requests = Request.query.filter_by(prod_id=result.id).all()

    return render_template("result.html", result=result, key=key,search_word=search_word,requests=requests)


@app.route('/summary')
def summary():
    all=requ=appr=deny=0
    all_requ=Request.query.all()
    for count in all_requ:
        all+=1
        if count.status=="approved":
            appr += 1
        elif count.status=="denied":
            deny +=1
        else:
            requ +=1  


    labels = ['Approved', 'Denied', 'Requested']
    values = [appr, deny, requ]

    plt.figure(figsize=(5,5))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Request Summary')

    # save image
    img_path = os.path.join('static', 'summary.png')
    plt.savefig(img_path)
    plt.close()

    return render_template("summary.html",deny=deny,appr=appr,all=all,requ=requ, img_path='summary.png')   