import pymysql
from django.contrib.auth.hashers import make_password, check_password
import os
from dotenv import load_dotenv
load_dotenv() 
def get_connection():
    return pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
class RentServices:

    # ================= REGISTER USER =================
    def addnewuser(self, full_name, email, password):
        try:
            con = get_connection()
            cursor = con.cursor()

            hashed_password = make_password(password)   

            query = "INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (full_name, email, hashed_password))

            con.commit()
            con.close()

            return "success"
        except Exception as e:
            print("DB ERROR:", e)
            return "failed"
        
 # ================= LOGIN USER =================
    def check_login(self, email, password):
        try:
            con = get_connection()
            cursor = con.cursor()

            query = "SELECT full_name, password FROM users WHERE email=%s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            con.close()

            if user and check_password(password, user[1]):  
                return user[0]
            else:
                return None
        except:
            return None
    
    # ================= ADD PROPERTY =================
    def add_property(self, user_email, name, type, location, rent, status):
        try:
            con = get_connection()            
            cursor = con.cursor()
            query = """
            INSERT INTO properties (user_email, name, type, location, rent, status)
            VALUES (%s,%s,%s,%s,%s,%s)
            """
            cursor.execute(query, (user_email, name, type, location, rent, status))
            con.commit()
            con.close()
            return "success"
        except Exception as e:
            print("DB ERROR:", e)
            return "failed"


# ================= GET USER PROPERTIES =================
    def get_properties(self, user_email):
        con = get_connection()        
        cursor = con.cursor(pymysql.cursors.DictCursor)
        query = "SELECT * FROM properties WHERE user_email=%s"
        cursor.execute(query, (user_email,))
        data = cursor.fetchall()
        con.close()
        return data
# ================= UPDATE PROPERTY =================
    def update_property(self, id, name, type, location, rent, status):
        con = get_connection()        
        cursor = con.cursor()
        query = """
        UPDATE properties
        SET name=%s, type=%s, location=%s, rent=%s, status=%s
        WHERE id=%s
        """
        cursor.execute(query, (name, type, location, rent, status, id))
        con.commit()
        con.close()
        
# ================= ADD TENANT  =================
    
    def add_tenant(self, user_email, name, phone, email, property_id):
        con = get_connection()        
        cursor = con.cursor()
        query = """
            INSERT INTO tenants (user_email, name, phone, email, property_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_email, name, phone, email, property_id))
        update_query = """
            UPDATE properties
            SET status='Occupied'
            WHERE id=%s
        """
        cursor.execute(update_query, (property_id,))

        con.commit()
        con.close()    
        
# ================= GET TENANTS INFORMATION =================

    def get_tenants(self, user_email):
        con = get_connection()        
        cursor = con.cursor(pymysql.cursors.DictCursor)

        query = """
        SELECT t.*, p.name AS property_name
        FROM tenants t
        LEFT JOIN properties p ON t.property_id = p.id
        WHERE t.user_email=%s
        """

        cursor.execute(query, (user_email,))
        data = cursor.fetchall()
        con.close()
        return data  
    # ================= UPDATE TENANT =================
    def update_tenant(self, tenant_id, name, phone, email):
        con = get_connection()
        cursor = con.cursor()

        query = """
        UPDATE tenants
        SET name=%s, phone=%s, email=%s
        WHERE id=%s
        """

        cursor.execute(query, (name, phone, email, tenant_id))
        con.commit()
        con.close()


# ================= DELETE TENANT =================
    def delete_tenant(self, tenant_id):
        con = get_connection()        
        cursor = con.cursor()
        cursor.execute("SELECT property_id FROM tenants WHERE id=%s", (tenant_id,))
        result = cursor.fetchone()

        if result and result[0]:
            property_id = result[0]
            cursor.execute("DELETE FROM tenants WHERE id=%s", (tenant_id,))
            cursor.execute("""
                UPDATE properties
                SET status='Vacant'
                WHERE id=%s
            """, (property_id,))
        else:
            cursor.execute("DELETE FROM tenants WHERE id=%s", (tenant_id,))

        con.commit()
        con.close()

# ================= GET VACENT PROPERTIES FOR TENANT =================
    def get_vacant_properties(self, user_email):
        con = get_connection()        
        cursor = con.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT * FROM properties
            WHERE user_email=%s AND status='Vacant'
        """
        cursor.execute(query, (user_email,))
        data = cursor.fetchall()
        con.close()
        return data
    
# ================= GET TENANT PAYMENT HISTORY =================
    def get_user_payments(self, user_email):
        try:
            con = get_connection()
            cursor = con.cursor(pymysql.cursors.DictCursor)
            query = """
        SELECT pay.id, t.name AS tenant_name, pr.name AS property_name,
            pay.month, pay.amount, pay.payment_date, pay.mode, pay.status,
            t.id AS tenant_id
        FROM payments pay
        JOIN tenants t ON pay.tenant_id = t.id
        JOIN properties pr ON pay.property_id = pr.id
        WHERE pay.user_email = %s
        ORDER BY pay.payment_date DESC
    """
            cursor.execute(query, (user_email,))
            data = cursor.fetchall()
            con.close()
            return data
        except Exception as e:
            print("DB ERROR:", e)
            return []
        
    def save_payment(self,user_email, tenant_id, month, amount, payment_date, mode, status):
        try:
            con = get_connection()            
            cursor = con.cursor()
            
            cursor.execute("SELECT property_id FROM tenants WHERE id=%s", (tenant_id,))
            result = cursor.fetchone()
            if not result:
                con.close()
                return "failed"
            
            property_id = result[0]

            query = """
        INSERT INTO payments 
        (user_email, tenant_id, property_id, month, amount, payment_date, mode, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
            cursor.execute(query, (user_email,tenant_id, property_id, month, amount, payment_date, mode, status))
            con.commit()
            con.close()
            return "success"

        except Exception as e:
            print("DB ERROR:", e)
            return "failed"
        
    # ================= GET SINGLE TENANT PAYMENT HISTORY =================
    def get_tenant_payments(self, tenant_id):
        try:
            con = get_connection()            
            cursor = con.cursor(pymysql.cursors.DictCursor)
            query = """
                SELECT pay.month,
                    pr.name AS property_name,
                    pay.amount,
                    pay.payment_date,
                    pay.mode,
                    pay.status
                FROM payments pay
                JOIN properties pr ON pay.property_id = pr.id
                WHERE pay.tenant_id = %s
                ORDER BY pay.payment_date DESC
            """
            cursor.execute(query, (tenant_id,))
            data = cursor.fetchall()
            con.close()
            return data
        except Exception as e:
            print("DB ERROR:", e)
            return []
        
    def add_agreement(self, user_email, tenant_id, property_id,monthly_rent, security_deposit,start_date, end_date, rent_due_day):

        con = get_connection()        
        cursor = con.cursor()
        query = """
            INSERT INTO agreements
            (user_email, tenant_id, property_id,
            monthly_rent, security_deposit,
            start_date, end_date, rent_due_day)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(query, (
            user_email, tenant_id, property_id,
            monthly_rent, security_deposit,
            start_date, end_date, rent_due_day
        ))
        con.commit()
        con.close()
        
    def get_agreements(self, user_email):
        con = get_connection()        
        cursor = con.cursor(pymysql.cursors.DictCursor)

        cursor = con.cursor(pymysql.cursors.DictCursor)
            
        query = """
                SELECT a.*, t.name AS tenant_name, p.name AS property_name
                FROM agreements a
                JOIN tenants t ON a.tenant_id = t.id
                JOIN properties p ON a.property_id = p.id
                WHERE a.user_email = %s
                ORDER BY a.start_date DESC
            """
        cursor.execute(query, (user_email,))
        data = cursor.fetchall()
        con.close()
        return data
        
    def update_agreement(self, agreement_id, tenant_id, property_id,monthly_rent, security_deposit,start_date, end_date, status):

        con = get_connection()
        cursor = con.cursor()

        query = """
            UPDATE agreements
            SET tenant_id=%s,
                property_id=%s,
                monthly_rent=%s,
                security_deposit=%s,
                end_date=%s,
                status=%s
            WHERE id=%s
        """

        cursor.execute(query, (
            tenant_id,
            property_id,
            monthly_rent,
            security_deposit,
            end_date,
            status,
            agreement_id
        ))

        con.commit()
        con.close()
        
    def get_dashboard_data(self, user_email):

        con = get_connection()        
        cursor = con.cursor()
        # Total Properties
        cursor.execute(
            "SELECT COUNT(*) FROM properties WHERE user_email=%s",
            (user_email,)
        )
        total_properties = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM tenants WHERE user_email=%s",
            (user_email,)
        )
        active_tenants = cursor.fetchone()[0]
        cursor.execute(
            "SELECT IFNULL(SUM(monthly_rent),0) FROM agreements WHERE user_email=%s AND status='Valid'",
            (user_email,)
        )
        monthly_rent = cursor.fetchone()[0]

        con.close()
        return {
            "total_properties": total_properties,
            "active_tenants": active_tenants,
            "monthly_rent": monthly_rent
        }
    
    def get_pending_payments(self, user_email):
        try:
            con = get_connection()
            cursor = con.cursor(pymysql.cursors.DictCursor)

            query = """
                SELECT 
                    t.name AS tenant_name,
                    p.name AS property_name,
                    pay.month,
                    pay.amount
                FROM payments pay
                JOIN tenants t ON pay.tenant_id = t.id
                JOIN properties p ON pay.property_id = p.id
                WHERE pay.user_email = %s AND pay.status = 'Pending'
            """

            cursor.execute(query, (user_email,))
            data = cursor.fetchall()
            con.close()
            return data

        except Exception as e:
            print("DB ERROR:", e)
            return []
        

    def get_all_payments_with_status(self, user_email):
        try:
            con = get_connection()
            cursor = con.cursor(pymysql.cursors.DictCursor)

            query = """
            SELECT 
                t.id AS tenant_id,
                t.name AS tenant_name,
                p.name AS property_name,
                COALESCE(a.monthly_rent, p.rent) AS amount,

                DATE_FORMAT(CURDATE(), '%%Y-%%m') AS month,

                pay.payment_date,
                pay.mode,

                CASE 
                    WHEN pay.status = 'Paid' THEN 'Paid'
                    ELSE 'Pending'
                END AS status

            FROM tenants t
            JOIN properties p ON t.property_id = p.id
            LEFT JOIN agreements a ON t.id = a.tenant_id

            LEFT JOIN payments pay 
                ON pay.id = (
                    SELECT id FROM payments 
                    WHERE tenant_id = t.id 
                    AND month = DATE_FORMAT(CURDATE(), '%%Y-%%m')
                    ORDER BY id DESC 
                    LIMIT 1
                )

            WHERE t.user_email = %s
            """

            cursor.execute(query, (user_email,))
            data = cursor.fetchall()

           

            con.close()
            return data

        except Exception as e:
            print("DB ERROR:", e)
            return []
        
    
    def find_user(self, email):
        try:
            con = get_connection()
            cursor = con.cursor(pymysql.cursors.DictCursor)

            query = "SELECT * FROM users WHERE LOWER(email)=LOWER(%s)"
            cursor.execute(query, (email,))

            user = cursor.fetchone()
            con.close()

            return user
        except Exception as e:
            print("DB ERROR:", e)
            return None
        
    def get_user_by_id(self, user_id):
        try:
            con = get_connection()
            cursor = con.cursor(pymysql.cursors.DictCursor)

            query = "SELECT * FROM users WHERE id=%s"
            cursor.execute(query, (user_id,))

            user = cursor.fetchone()
            con.close()

            return user
        except Exception as e:
            print("DB ERROR:", e)
            return None