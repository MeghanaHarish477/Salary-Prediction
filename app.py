from flask import Flask, request, render_template_string
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import io
import base64
app = Flask(__name__)
data = pd.DataFrame({
    'Experience': [1, 2, 3, 4, 5, 6, 7, 8, 3, 5],
    'Performance': [3, 4, 4, 5, 5, 4, 5, 5, 3, 4],
    'Overtime_Hours': [5, 8, 10, 12, 15, 10, 18, 20, 5, 10],
    'Education': [1, 1, 2, 2, 2, 3, 3, 3, 1, 2],
    'Salary': [25000, 30000, 38000, 45000, 52000, 60000, 72000, 85000, 32000, 48000]
})
X = data[['Experience', 'Performance', 'Overtime_Hours', 'Education']]
y = data['Salary']
model = LinearRegression()
model.fit(X, y)
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Advanced Payroll Analytics</title>
    <style>
        body { font-family: 'Segoe UI', Arial; background: #f0f2f5; text-align: center; padding: 20px; }
        .container { background: white; max-width: 600px; margin: auto; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        input, select, button { width: 95%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { background: #2c3e50; color: white; border: none; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:hover { background: #34495e; }
        .result-box { margin-top: 20px; padding: 15px; background: #e8f5e9; border-radius: 8px; }
        img { max-width: 100%; height: auto; margin-top: 20px; border-radius: 8px; }
        label { display: block; text-align: left; font-weight: bold; margin-left: 15px; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📊 Employee Payroll Prediction</h2>
        <form method="POST">
            <label>Experience (Years)</label>
            <input type="number" name="experience" placeholder="e.g. 5" required>
            <label>Performance Rating (1-5)</label>
            <input type="number" name="performance" min="1" max="5" placeholder="e.g. 4" required>
            <label>Monthly Overtime Hours</label>
            <input type="number" name="overtime" placeholder="e.g. 10" required>
            <label>Education Level</label>
            <select name="education">
                <option value="1">Bachelor's Degree</option>
                <option value="2">Master's Degree</option>
                <option value="3">PhD</option>
            </select>
            <label>Department</label>
            <select name="department">
                <option value="IT">IT</option>
                <option value="HR">HR</option>
                <option value="Sales">Sales</option>
                <option value="Finance">Finance</option>
            </select>
            <button type="submit">Analyze & Predict Salary</button>
        </form>
        {% if prediction %}
            <div class="result-box">
                <h3>{{ prediction }}</h3>
                <p>Department: {{ dept_name }}</p>
            </div>
            <h4>Salary Comparison by Department</h4>
            <img src="data:image/png;base64,{{ chart_url }}">
        {% endif %}
    </div>
</body>
</html>
"""
def generate_chart(pred_salary, dept_name):
    depts = ['IT', 'HR', 'Sales', 'Finance']
    avg_salaries = [55000, 45000, 48000, 52000]
    
    if dept_name in depts:
        idx = depts.index(dept_name)
        avg_salaries[idx] = pred_salary

    plt.figure(figsize=(8, 5))
    plt.style.use('seaborn-v0_8-muted')
    colors = ['#bdc3c7' if d != dept_name else '#f39c12' for d in depts]
    bars = plt.bar(depts, avg_salaries, color=colors, edgecolor='white', linewidth=0.7)
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1000, 
                 f'₹{yval:,.0f}', ha='center', va='bottom', 
                 fontsize=10, fontweight='bold', color='#2c3e50')

    plt.ylabel('Monthly Salary (₹)', fontsize=11, fontweight='bold', color='#34495e')
    plt.title(f'Salary Analysis for {dept_name} Department', fontsize=14, pad=20, fontweight='bold')
    plt.ylim(0, max(avg_salaries) + 15000)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()
@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    chart_url = None
    dept_name = None
    if request.method == "POST":
        exp = float(request.form["experience"])
        perf = float(request.form["performance"])
        ot = float(request.form["overtime"])
        edu = float(request.form["education"])
        dept_name = request.form["department"]

        salary = model.predict([[exp, perf, ot, edu]])[0]
        prediction = f"Predicted Salary: ₹{salary:,.2f}"
        chart_url = generate_chart(salary, dept_name)
    return render_template_string(HTML_PAGE, prediction=prediction, chart_url=chart_url, dept_name=dept_name)

if __name__ == "__main__":
    app.run(debug=True) 
    app.run(debug=True)