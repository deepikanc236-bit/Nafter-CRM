# Nafter CRM: Role-Based Access Control (RBAC) & Security Walkthrough

This document outlines the enhanced security features and RBAC implementation for the Nafter CRM, specifically tailored for deployment on Render.

## 🔐 Security Improvements

### 1. Role-Specific Password Persistence
We have implemented a robust seeding logic in `final_seed.py` that respects manual changes made via the Django Admin.

- **Initial Setup:** On the first deployment, the system creates default accounts for each role (Manager, Senior Exec, Junior Exec) using environment variables (e.g., `SALES_MANAGER_PASSWORD`).
- **Persistence:** If you change a password in the Admin Panel, the seeding script **will not** overwrite it on subsequent deployments. It only sets passwords for *newly created* users.
- **Environment Variables:**
  - `sales_manager`: Password for `sales_manager`
  - `senior_sales_executives`: Password for `senior_sales_executives`
  - `sales_executives`: Password for `sales_executives`
  - `DJANGO_SUPERUSER_PASSWORD`: Fallback for all roles and default for superuser.

### 2. Diagnostic Cleanup
All development-only diagnostic endpoints (e.g., `/test-routing/`) have been removed to minimize the attack surface of the production application.

---

## 👥 RBAC Visibility Rules

The CRM automatically filters lead data based on the logged-in user's role:

| Role | Visibility Rule | Description |
| :--- | :--- | :--- |
| **Sales Manager** | All Leads | Full access to all leads across all budgets. |
| **Senior Sales Executive** | ₹5L - ₹10L | Can only see leads with budgets between 5 Lakhs and 10 Lakhs INR. |
| **Sales Executive** | < ₹5L | Can only see leads with budgets under 5 Lakhs INR. |
| **Any Staff** | Assigned Only | Always sees leads that are explicitly assigned to them, regardless of budget. |

---

## 🚀 Deployment (Render)

### Procfile Configuration
The `Procfile` is configured to run the seeding script before starting the web server:
```bash
web: python3 final_seed.py && gunicorn config.wsgi
```
This ensures that the necessary groups and default users exist on every deployment.

### 🛠️ Manual Steps Required

To ensure your CRM is fully functional and secure on Render, you **must** manually configure the following in the Render Dashboard (Environment tab):

1. **Role Passwords:** Set `sales_manager`, `senior_sales_executives`, and `sales_executives`.
2. **Persistence Key:** Set `DJANGO_SUPERUSER_PASSWORD` (used as a fallback and for the main admin).
3. **Core Django Settings:**
   - `SECRET_KEY`: A long, random string.
   - `DEBUG`: Set to `False`.
   - `DATABASE_URL`: Your Render Postgres connection string.
4. **Site URL:** Set `SITE_URL` to your production domain (e.g., `https://nafter-crm.onrender.com`) for correct email links.

**Everything else (Database migrations, static files, role creation, and permission setup) is automated.**

---

*Handover complete. The system is now fully secured and ready for production use.*
