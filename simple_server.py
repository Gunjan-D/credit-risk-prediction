#!/usr/bin/env python3
"""
Simple HTTP Server to run the Credit Risk Prediction App on localhost:3000
This uses only Python standard library - no Flask needed!
"""

import http.server
import socketserver
import urllib.parse
import json
import os
from pathlib import Path

class CreditRiskHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            # Serve the main form
            self.serve_file('Final/Reportfiles/templates/Index.html')
        elif self.path == '/results.html':
            # Serve results page
            self.serve_file('Final/Reportfiles/templates/results.html')
        else:
            # Serve static files
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/predict':
            # Handle form submission
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse form data
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Extract form values
            person_age = form_data.get('person_age', [''])[0]
            person_income = form_data.get('person_income', [''])[0]
            loan_amnt = form_data.get('loan_amnt', [''])[0]
            
            # Simple demo prediction logic (replace with actual ML model later)
            prediction = self.simple_prediction(form_data)
            
            # Generate results page
            self.serve_results(prediction, form_data)
        else:
            self.send_error(404)
    
    def simple_prediction(self, form_data):
        """More realistic demo prediction - replace with your ML model"""
        try:
            age = float(form_data.get('person_age', ['30'])[0])
            income = float(form_data.get('person_income', ['50000'])[0])
            loan_amount = float(form_data.get('loan_amnt', ['15000'])[0])
            employment_length = float(form_data.get('person_emp_length', ['5'])[0])
            
            # Start with base score
            score = 50
            
            # Age factor
            if age >= 25 and age <= 65: score += 10
            
            # Income factor
            if income >= 40000: score += 15
            if income >= 60000: score += 10
            
            # Employment stability
            if employment_length >= 2: score += 10
            if employment_length >= 5: score += 5
            
            # Debt-to-income ratio (very important)
            loan_to_income_ratio = loan_amount / income
            if loan_to_income_ratio <= 0.1: score += 20
            elif loan_to_income_ratio <= 0.2: score += 10
            elif loan_to_income_ratio <= 0.3: score += 5
            elif loan_to_income_ratio > 0.5: score -= 20
            
            # Home ownership
            home_ownership = form_data.get('person_home_ownership', ['RENT'])[0]
            if home_ownership == 'OWN': score += 15
            elif home_ownership == 'MORTGAGE': score += 10
            elif home_ownership == 'RENT': score += 0
            else: score -= 5
            
            # Loan grade (very important)
            loan_grade = form_data.get('loan_grade', ['C'])[0]
            grade_scores = {'A': 25, 'B': 15, 'C': 5, 'D': -5, 'E': -15, 'F': -25, 'G': -35}
            score += grade_scores.get(loan_grade, 0)
            
            # Loan intent
            loan_intent = form_data.get('loan_intent', ['PERSONAL'])[0]
            if loan_intent in ['EDUCATION', 'HOMEIMPROVEMENT']: score += 5
            elif loan_intent == 'DEBTCONSOLIDATION': score -= 10
            elif loan_intent in ['MEDICAL', 'PERSONAL']: score += 0
            elif loan_intent == 'VENTURE': score -= 5
            
            # Default history (CRITICAL FACTOR)
            default_history = form_data.get('cb_person_default_on_file', ['N'])[0]
            if default_history == 'Y': 
                score -= 40  # Major penalty for previous default
            else: 
                score += 15
            
            # Credit history length
            try:
                credit_hist = float(form_data.get('cb_person_cred_hist_length', ['5'])[0])
                if credit_hist >= 10: score += 10
                elif credit_hist >= 5: score += 5
                elif credit_hist < 2: score -= 10
            except:
                pass
            
            return 'Approved' if score >= 70 else 'Rejected'
            
        except Exception as e:
            return 'Rejected'
    
    def serve_file(self, filepath):
        """Serve a file with proper content type"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            self.send_error(404, f"File not found: {filepath}")
    
    def serve_results(self, prediction, form_data):
        """Generate and serve results page"""
        
        # Create explanation based on prediction
        if prediction == 'Approved':
            explanation = """✅ **Loan Approved!**

**Positive Factors:**
1. **Stable Employment**: Your employment history shows reliability
2. **Adequate Income**: Your income level supports loan repayment
3. **Reasonable Loan Amount**: The requested amount is within acceptable limits
4. **Credit Profile**: Your credit profile meets our approval criteria

**Next Steps:**
- You will receive loan documents via email
- Review and sign the agreement
- Funds will be disbursed within 3-5 business days"""
        else:
            explanation = """❌ **Loan Application Rejected**

**Areas for Improvement:**
1. **Income**: Consider increasing your annual income
2. **Employment History**: Maintain stable employment for at least 2 years
3. **Loan Amount**: Request a smaller loan amount relative to your income
4. **Credit History**: Work on improving your credit score

**Suggestions:**
- Pay down existing debts
- Maintain consistent employment
- Consider a co-signer for your application
- Apply again after 6 months of financial improvement"""

        # Generate results HTML
        results_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loan Prediction Results</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css">
    <style>
        body {{ background-color: #f5f5f5; }}
        .header {{
            background: linear-gradient(90deg, #003366, #00509e);
            color: white; padding: 20px; text-align: center;
            font-size: 36px; font-weight: bold;
        }}
        .result-container.approved {{
            background-color: #d4edda; color: #155724;
        }}
        .result-container.rejected {{
            background-color: #f8d7da; color: #721c24;
        }}
        .result-container {{
            border-radius: 10px; padding: 20px; margin-top: 30px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
        }}
        .suggestions {{
            background-color: #003366; color: white; padding: 20px;
            border-radius: 10px; margin-top: 20px;
        }}
        .pre-formatted {{ white-space: pre-line; }}
    </style>
</head>
<body>
    <div class="header">🏦 Loan Prediction Results</div>
    <div class="container">
        <div class="result-container {'approved' if prediction == 'Approved' else 'rejected'}">
            <h3>Prediction: <strong>{prediction}</strong></h3>
        </div>
        <div class="suggestions">
            <h5>Analysis & Explanation:</h5>
            <p class="pre-formatted">{explanation}</p>
        </div>
        <div class="text-center mt-4">
            <a href="/" class="btn btn-secondary">🔙 Apply Again</a>
        </div>
        
        <div class="card mt-4">
            <div class="card-header">📊 Your Application Details</div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Age:</strong> {form_data.get('person_age', ['N/A'])[0]}</p>
                        <p><strong>Income:</strong> ${form_data.get('person_income', ['N/A'])[0]}</p>
                        <p><strong>Employment:</strong> {form_data.get('person_emp_length', ['N/A'])[0]} years</p>
                        <p><strong>Loan Amount:</strong> ${form_data.get('loan_amnt', ['N/A'])[0]}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Home Ownership:</strong> {form_data.get('person_home_ownership', ['N/A'])[0]}</p>
                        <p><strong>Loan Purpose:</strong> {form_data.get('loan_intent', ['N/A'])[0]}</p>
                        <p><strong>Loan Grade:</strong> {form_data.get('loan_grade', ['N/A'])[0]}</p>
                        <p><strong>Default History:</strong> {form_data.get('cb_person_default_on_file', ['N/A'])[0]}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(results_html.encode('utf-8'))

def main():
    PORT = 3000
    
    # Change to the correct directory
    os.chdir('C:\\Users\\gdeshpande\\Downloads\\AMS560_project copy')
    
    # Create server
    with socketserver.TCPServer(("", PORT), CreditRiskHandler) as httpd:
        print(f"🚀 Credit Risk Prediction Server running at http://localhost:{PORT}")
        print(f"📋 Open your browser and go to: http://localhost:{PORT}")
        print("🔄 Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\n⏹️ Server stopped")

if __name__ == "__main__":
    main()