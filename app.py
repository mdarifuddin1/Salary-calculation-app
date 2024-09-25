import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

def calculate_salary(name, hourly_rate, required_hours, hours_worked):
    total_salary = required_hours * hourly_rate
    
    if hours_worked >= required_hours:
        status = "No"
        hours_deducted = 0
        deduction_amount = 0
    else:
        status = "Yes"
        hours_deducted = required_hours - hours_worked
        deduction_amount = hours_deducted * hourly_rate
    
    actual_salary = total_salary - deduction_amount
    
    return {
        "Name": name,
        "Hourly Rate": hourly_rate,
        "Required Hours": required_hours,
        "Hours Worked": hours_worked,
        "Total Salary": total_salary,
        "Salary Cut Status": status,
        "Hours Deducted": hours_deducted,
        "Amount Deducted (Tk)": deduction_amount,
        "Actual Salary": actual_salary
    }

def generate_pdf(results):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Salary Calculation Result", styles['Title'])
    elements.append(title)

    data = [["Name", "Hourly Rate", "Required Hours", "Hours Worked", "Total Salary", "Salary Cut", "Hours Deducted", "Amount Deducted", "Actual Salary"]]
    
    for result in results:
        data.append([
            result['Name'],
            f"{result['Hourly Rate']:.2f}",
            f"{result['Required Hours']:.2f}",
            f"{result['Hours Worked']:.2f}",
            f"{result['Total Salary']:.2f}",
            result['Salary Cut Status'],
            f"{result['Hours Deducted']:.2f}",
            f"{result['Amount Deducted (Tk)']:.2f}",
            f"{result['Actual Salary']:.2f}"
        ])
    
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    
    # Adjust table column widths
    col_widths = [70, 70, 80, 70, 70, 70, 80, 90, 70]
    for i, width in enumerate(col_widths):
        table._argW[i] = width

    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Streamlit app
st.title("Employee Salary Calculation App")

# Initialize session state for employees
if 'employees' not in st.session_state:
    st.session_state.employees = []

# User input
with st.form("employee_form"):
    name = st.text_input("Employee Name")
    hourly_rate = st.number_input("Hourly Rate", min_value=0.0, step=0.01)
    required_hours = st.number_input("Required Hours for 1 Month", min_value=0.0, step=0.1)
    hours_worked = st.number_input("Hours Worked in Month", min_value=0.0, step=0.1)
    
    submit_button = st.form_submit_button(label='Add Employee')

if submit_button:
    if name and hourly_rate > 0 and required_hours > 0 and hours_worked >= 0:
        employee_data = calculate_salary(name, hourly_rate, required_hours, hours_worked)
        st.session_state.employees.append(employee_data)
        st.success(f"Employee {name} added successfully!")
    else:
        st.error("Please fill in all fields with valid values.")

if st.session_state.employees:
    st.subheader("Employee List")
    st.table(pd.DataFrame(st.session_state.employees))
    
    if st.button("Generate PDF Report"):
        pdf_buffer = generate_pdf(st.session_state.employees)
        
        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="salary_report.pdf",
            mime="application/pdf"
        )

    if st.button("Clear All Employees"):
        st.session_state.employees = []
        st.success("All employees cleared!")