from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import RentServices
import pandas as pd
import numpy as np

# ================= GET PROPERTIES =================
@api_view(['GET'])
def api_get_properties(request):
    user_email = request.GET.get('email')

    if not user_email:
        return Response({"error": "Email required"}, status=400)

    data = RentServices().get_properties(user_email)
    return Response(data)


# ================= GET TENANTS =================
@api_view(['GET'])
def api_get_tenants(request):
    user_email = request.GET.get('email')

    if not user_email:
        return Response({"error": "Email required"}, status=400)

    data = RentServices().get_tenants(user_email)
    return Response(data)


# ================= GET PAYMENTS =================
@api_view(['GET'])
def api_get_payments(request):
    user_email = request.GET.get('email')
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 5))

    if not user_email:
        return Response({"error": "Email required"}, status=400)

    service = RentServices()
    payments = service.get_user_payments(user_email)

    df = pd.DataFrame(payments)

    if df.empty:
        return Response({"data": [], "total": 0})

    #  SEARCH
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    # FILTER
    if status:
        df = df[df['status'] == status]

    #  PAGINATION
    total = len(df)

    start = (page - 1) * limit
    end = start + limit

    df = df.iloc[start:end]

    return Response({
        "data": df.to_dict(orient='records'),
        "total": total,
        "page": page
    })




@api_view(['GET'])
def api_dashboard_analytics(request):
    user_email = request.session.get("email")

    if not user_email:
        return Response({"error": "Unauthorized"}, status=401)

    service = RentServices()

    properties = service.get_properties(user_email)
    tenants = service.get_tenants(user_email)
    payments = service.get_user_payments(user_email)

    # ================= CONVERT TO DATAFRAME =================
    df_properties = pd.DataFrame(properties)
    df_tenants = pd.DataFrame(tenants)
    df_payments = pd.DataFrame(payments)

    # ================= BASIC SAFETY =================
    if df_payments.empty:
        return Response({"message": "No data available"})

    # ================= CLEANING =================
    df_payments['amount'] = pd.to_numeric(df_payments['amount'], errors='coerce')
    df_payments['month'] = df_payments['month'].astype(str)

    # ================= TOTAL REVENUE =================
    total_revenue = df_payments[df_payments['status'] == 'Paid']['amount'].sum()

    # ================= MONTHLY REVENUE =================
    monthly_revenue = (
    df_payments
    .groupby('month')['amount']
    .sum()
    .reset_index()
    .sort_values('month')
)

    months = monthly_revenue['month'].astype(str).tolist()
    revenue_data = monthly_revenue['amount'].tolist()

    # ================= OCCUPANCY =================
    total_properties = len(df_properties)
    occupied = len(df_properties[df_properties['status'] == 'Occupied'])

    occupancy_rate = (occupied / total_properties * 100) if total_properties > 0 else 0

    # ================= PENDING PAYMENTS =================
    pending_payments = len(df_payments[df_payments['status'] != 'Paid'])

    # ================= ADVANCED INSIGHTS =================
    avg_rent = np.mean(df_payments['amount'])

    max_payment = df_payments['amount'].max()
    min_payment = df_payments['amount'].min()
    insights = []

# 1. Revenue Growth %
    if len(monthly_revenue) > 1:
        last_month = monthly_revenue.iloc[-1]['amount']
        prev_month = monthly_revenue.iloc[-2]['amount']

        if prev_month > 0:
            growth = ((last_month - prev_month) / prev_month) * 100

            if growth > 0:
                insights.append(f"📈 Revenue increased by {round(growth, 2)}%")
            else:
                insights.append(f"📉 Revenue decreased by {round(abs(growth), 2)}%")

# 2. Occupancy Insight
    if occupancy_rate >= 80:
        insights.append(f"🏠 High occupancy: {round(occupancy_rate, 2)}% properties occupied")
    else:
        insights.append(f"🏠 {round(occupancy_rate, 2)}% properties occupied")

    # 3. Pending Payments
    if pending_payments > 0:
        insights.append(f"⚠️ {pending_payments} payments pending")
    else:
        insights.append("✅ All payments are completed")

# 4. High Value Alert
    if max_payment > avg_rent:
        insights.append(" High-value payments detected")

    return Response({
        "total_revenue": int(total_revenue),
        "occupancy_rate": round(occupancy_rate, 2),
        "pending_payments": int(pending_payments),

        "months": months,
        "revenue_data": revenue_data,

        "average_payment": int(avg_rent),
        "highest_payment": int(max_payment),
        "lowest_payment": int(min_payment),

        "insights": insights   
    })


