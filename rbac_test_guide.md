# RBAC Test Guide (Nafter CRM)

This guide helps you verify that the Role-Based Access Control (RBAC) system is correctly filtering lead data based on user groups and lead budgets.

## 1. Create Test Users
Log in to your [Admin Panel](https://nafter-crm.onrender.com/admin/) and create three "Staff" users for testing:

1.  **Manager User:** Add to the `Sales Managers` group.
2.  **Senior Exec User:** Add to the `Senior Sales Executives` group.
3.  **Junior Exec User:** Add to the `Sales Executives` group.

> [!IMPORTANT]
> Ensure the **"Staff status"** checkbox is checked for all test users so they can log in to the CRM.

## 2. Verify Visibility Rules
Log in as each user at `https://nafter-crm.onrender.com/dashboard/` and verify the following:

| Role | Visibility Rule | Expected Outcome |
| :--- | :--- | :--- |
| **Superuser / Manager** | All Leads | Should see **all** leads in the system. |
| **Senior Sales Exec** | ₹5L to ₹10L | Should only see leads with budgets between **₹5,00,000** and **₹10,00,000**. |
| **Sales Exec** | Under ₹5L | Should only see leads with budgets **under ₹5,00,000**. |
| **Generic User** | Assigned Only | Should only see leads that have been **specifically assigned** to them. |

## 3. Test Lead Re-assignment
1. Log in as a **Sales Manager**. 
2. Go to a Lead's detail page.
3. You should see an **"Assign Lead"** dropdown.
4. Try assigning a lead to a Senior or Junior executive.
5. Log in as that executive to verify they can now see that specific lead regardless of the budget rule.

## 4. Admin Panel Security
Visit `https://nafter-crm.onrender.com/admin/` with a non-superuser account. 
- **Expected:** You should be automatically redirected to the `/dashboard/`.
