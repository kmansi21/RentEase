from django.shortcuts import render,redirect
from django.views.decorators.cache import never_cache
from .services import RentServices
from django.contrib import messages
from django.http import JsonResponse

def home(request):
    return render(request,"index.html")


def adduser(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        obj = RentServices()
        msg = obj.addnewuser(full_name, email, password)
        if msg == "success":
            messages.success(request, "Account created successfully!")
        else:
            messages.error(request, "Registration failed!")
        return redirect("/register/")
    return render(request, "register.html")


def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        obj = RentServices()
        user_name = obj.check_login(email, password)

        if user_name:
            request.session["name"] = user_name
            request.session["email"] = email
            request.session.set_expiry(3600)
            # messages.success(request, {user_name})
            return redirect("/dashboard/")  
        else:
            messages.error(request, "Invalid Email or Password")
            return redirect("/login/")  

    return render(request, "login.html")


def dashboard(request):
    if "email" not in request.session:
        return redirect("/login/")

    name = request.session["name"]
    user_email = request.session["email"]

    obj = RentServices()
    data = obj.get_dashboard_data(user_email)
    pending_payments = obj.get_pending_payments(user_email)

    return render(request, "dashboard.html", {
        "name": name,
        "total_properties": data["total_properties"],
        "active_tenants": data["active_tenants"],
        "monthly_rent": data["monthly_rent"],
        "pending_payments": pending_payments
    })


def property(request):
    if "email" not in request.session:
        return redirect("/login/")

    user_email = request.session["email"]
    obj = RentServices()
    properties = obj.get_properties(user_email)

    return render(request, "property.html", {"properties": properties})
    
    
def add_property(request):
    if request.method == "POST":
        user_email = request.session["email"]
        name = request.POST.get("name")
        type = request.POST.get("type")
        location = request.POST.get("location")
        rent = request.POST.get("rent")
        status = request.POST.get("status")

        obj = RentServices()
        result=obj.add_property(user_email, name, type, location, rent, status)
        if result == "success":
                messages.success(request, "Property added successfully")
        else:
            messages.error(request, "Something went wrong ")
    return redirect("/property/")


def edit_property(request):
    if request.method == "POST":
        id = request.POST.get("id")
        name = request.POST.get("name")
        type = request.POST.get("type")
        location = request.POST.get("location")
        rent = request.POST.get("rent")
        status = request.POST.get("status")

        obj = RentServices()
        obj.update_property(id, name, type, location, rent, status)

        messages.success(request, "Property updated successfully")

    return redirect("/property/")


def tenant(request):
    if "email" not in request.session:
        return redirect("/login/")

    user_email = request.session["email"]
    obj = RentServices()

    tenants = obj.get_tenants(user_email)
    properties = obj.get_vacant_properties(user_email)

    return render(request, "tenants.html", {
        "tenants": tenants,
        "properties": properties
    })
    
    
def add_tenant(request):
    if "email" not in request.session:
        return redirect("/login/")

    if request.method == "POST":
        user_email = request.session["email"]
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        property_id = request.POST.get("property_id")

        obj = RentServices()
        obj.add_tenant(user_email, name, phone, email, property_id)

        messages.success(request, "Tenant added successfully")

    return redirect("/tenant/")

def update_tenant(request):
    if request.method == "POST":
        id = request.POST.get("id")
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        obj = RentServices()
        obj.update_tenant(id, name, phone, email)

        messages.success(request, "Tenant updated successfully")

    return redirect("/tenant/")


def delete_tenant(request, id):
    obj = RentServices()
    obj.delete_tenant(id)
    messages.success(request, "Tenant deleted successfully")
    return redirect("/tenant/")

def payment(request):
    if "email" not in request.session:
        return redirect("/login/")

    user_email = request.session["email"]
    obj = RentServices()
    tenants = obj.get_tenants(user_email)
    properties = obj.get_properties(user_email)
    payments = obj.get_all_payments_with_status(user_email)

    return render(request, "payments.html", {
        "tenants": tenants,
        "properties": properties,
        "payments": payments
    })


def add_payment(request):
    if "email" not in request.session:
        return redirect("/login/")

    if request.method == "POST":
        user_email = request.session["email"]
        tenant_id = request.POST.get("tenant_id")
        month = request.POST.get("month")
        amount = request.POST.get("amount")
        payment_date = request.POST.get("payment_date")
        mode = request.POST.get("mode")
        status = "Paid"

        obj = RentServices()
        tenants = obj.get_tenants(user_email)
        valid_tenant_ids = [str(t["id"]) for t in tenants]

        if tenant_id not in valid_tenant_ids:
            messages.error(request, "Unauthorized payment attempt!")
            return redirect("/payment/")

        result = obj.save_payment(
            user_email, tenant_id, month, amount, payment_date, mode, status
        )

        if result == "success":
            messages.success(request, "Payment saved successfully")
        else:
            messages.error(request, "Failed to save payment")

    return redirect("/payment/")


def tenant_history(request, tenant_id):
    obj = RentServices()
    history = obj.get_tenant_payments(tenant_id)
    return JsonResponse(history, safe=False)


def agreement(request):
    if "email" not in request.session:
        return redirect("/login/")
    
    user_email = request.session["email"]  
    obj = RentServices()
    agreements = obj.get_agreements(user_email)
    tenants = obj.get_tenants(user_email)
    properties = obj.get_properties(user_email)
    
    return render(request, "agreements.html", {
        "agreements": agreements,
        "tenants": tenants,
        "properties": properties
    })
def add_agreement(request):
    if request.method == "POST":
        user_email = request.session["email"]

        tenant_id = request.POST.get("tenant_id")
        property_id = request.POST.get("property_id")
        monthly_rent = request.POST.get("monthly_rent")
        security_deposit = request.POST.get("security_deposit")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        rent_due_day = request.POST.get("rent_due_day")

        obj = RentServices()
        obj.add_agreement(
            user_email, tenant_id, property_id,
            monthly_rent, security_deposit,
            start_date, end_date, rent_due_day
        )

        messages.success(request, "Agreement created successfully")

    return redirect("/agreement/")

def update_agreement(request):
    if request.method == "POST":
        obj = RentServices()

        obj.update_agreement(
            request.POST["agreement_id"],
            request.POST["tenant_id"],
            request.POST["property_id"],
            request.POST["monthly_rent"],
            request.POST["security_deposit"],
            request.POST["end_date"],
            request.POST["status"]
        )
        messages.success(request, "Agreement updated successfully")
    return redirect("/agreement/")



def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        obj = RentServices()
        user = obj.find_user(email)

        if user:
            request.session['reset_user_id'] = user['id']
            return redirect('/reset-password/')
        else:
            messages.error(request, "Email not found")

    return render(request, "forgot_password.html")

def reset_password(request):
    user_id = request.session.get('reset_user_id')

    if not user_id:
        return redirect('/forgot-password/')

    obj = RentServices()
    user = obj.get_user_by_id(user_id)

    if request.method == "POST":
        name = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        result = obj.update_user_credentials(user_id, name, email, password)

        if result == "success":
            del request.session['reset_user_id']
            messages.success(request, "Details updated successfully")
            return redirect('/login/')
        else:
            messages.error(request, "Update failed")

    return render(request, "reset_password.html", {"user": user})


def logout_view(request):
    request.session.flush()   
    return redirect("/")