#!/usr/bin/env python3
"""
Fast and Simple Credit Risk Prediction Server
Optimized for quick loading on localhost:3000
"""

import http.server
import socketserver
import urllib.parse
import json
import os
from pathlib import Path

# Simple HTML template for the form
FORM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏦 Credit Risk Prediction</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .main-container { background: white; border-radius: 15px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); margin: 20px auto; max-width: 1000px; }
        .header { background: linear-gradient(45deg, #1e3c72, #2a5298); color: white; padding: 30px; text-align: center; border-radius: 15px 15px 0 0; }
        .form-section { padding: 30px; }
        .btn-predict { background: linear-gradient(45deg, #1e3c72, #2a5298); border: none; padding: 12px 40px; font-size: 18px; border-radius: 25px; }
        .disclaimer { background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-container">
            <div class="header">
                <h1>🏦 Credit Risk Prediction System</h1>
                <p>Advanced ML-powered Loan Assessment</p>
            </div>
            
            <div class="form-section">
                <div class="disclaimer">
                    <strong>📊 AI-Powered Analysis:</strong> This system uses machine learning to evaluate loan applications based on multiple risk factors including credit history, income, and employment stability.
                </div>
                
                <form method="POST" action="/predict" class="needs-validation" novalidate>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">👤 Age</label>
                            <input type="number" name="person_age" class="form-control" placeholder="Enter age (e.g., 30)" required min="18" max="100">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">💰 Annual Income ($)</label>
                            <input type="number" name="person_income" class="form-control" placeholder="Enter income (e.g., 50000)" required min="1000">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">💼 Employment Length (Years)</label>
                            <input type="number" name="person_emp_length" class="form-control" placeholder="Years (e.g., 5.5)" required min="0" step="0.1">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">💵 Loan Amount ($)</label>
                            <input type="number" name="loan_amnt" class="form-control" placeholder="Amount (e.g., 15000)" required min="100">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">📊 Interest Rate (%)</label>
                            <input type="number" name="loan_int_rate" class="form-control" placeholder="Rate (e.g., 7.5)" required min="0" step="0.1">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">📈 Loan % of Income</label>
                            <input type="number" name="loan_percent_income" class="form-control" placeholder="Percentage (e.g., 0.3)" required min="0" max="1" step="0.01">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">📋 Credit History Length (Years)</label>
                            <input type="number" name="cb_person_cred_hist_length" class="form-control" placeholder="Years (e.g., 10)" required min="0">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">🏠 Home Ownership</label>
                            <select name="person_home_ownership" class="form-select" required>
                                <option value="">Select ownership type</option>
                                <option value="RENT">🏢 Rent</option>
                                <option value="MORTGAGE">🏠 Mortgage</option>
                                <option value="OWN">🏡 Own</option>
                                <option value="OTHER">🏘️ Other</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">🎯 Loan Purpose</label>
                            <select name="loan_intent" class="form-select" required>
                                <option value="">Select purpose</option>
                                <option value="PERSONAL">👤 Personal</option>
                                <option value="EDUCATION">🎓 Education</option>
                                <option value="MEDICAL">🏥 Medical</option>
                                <option value="VENTURE">🚀 Business</option>
                                <option value="HOMEIMPROVEMENT">🔨 Home Improvement</option>
                                <option value="DEBTCONSOLIDATION">💳 Debt Consolidation</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">⭐ Loan Grade</label>
                            <select name="loan_grade" class="form-select" required>
                                <option value="">Select grade</option>
                                <option value="A">A - Excellent</option>
                                <option value="B">B - Very Good</option>
                                <option value="C">C - Good</option>
                                <option value="D">D - Fair</option>
                                <option value="E">E - Poor</option>
                                <option value="F">F - Very Poor</option>
                                <option value="G">G - High Risk</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">⚠️ Previous Default</label>
                            <select name="cb_person_default_on_file" class="form-select" required>
                                <option value="">Select history</option>
                                <option value="N">❌ No Default History</option>
                                <option value="Y">⚠️ Previous Default</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="text-center mt-4">
                        <button type="submit" class="btn btn-primary btn-predict">
                            🔮 Analyze Credit Risk
                        </button>
                    </div>
                </form>
                
                <div class="disclaimer mt-4">
                    <strong>⚠️ Disclaimer:</strong> This is an educational demo using machine learning models trained on sample data. Results should not be used for actual financial decisions.
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

class FastCreditRiskHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/' or self.path.startswith('/?'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(FORM_HTML.encode('utf-8'))
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/predict':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
                
                prediction, explanation = self.predict_loan(form_data)
                self.serve_results(prediction, explanation, form_data)
                
            except Exception as e:
                self.send_error(500, f"Server error: {str(e)}")
        else:
            self.send_error(404)
    
    def predict_loan(self, form_data):
        """Enhanced prediction with detailed scoring"""
        try:
            # Extract and validate inputs
            age = float(form_data.get('person_age', ['30'])[0])
            income = float(form_data.get('person_income', ['50000'])[0])
            loan_amount = float(form_data.get('loan_amnt', ['15000'])[0])
            employment_length = float(form_data.get('person_emp_length', ['5'])[0])
            credit_history = float(form_data.get('cb_person_cred_hist_length', ['5'])[0])
            
            # Categorical variables
            home_ownership = form_data.get('person_home_ownership', ['RENT'])[0]
            loan_intent = form_data.get('loan_intent', ['PERSONAL'])[0]
            loan_grade = form_data.get('loan_grade', ['C'])[0]
            default_history = form_data.get('cb_person_default_on_file', ['N'])[0]
            
            score = 50  # Base score
            factors = []
            
            # Age scoring
            if 25 <= age <= 65:
                score += 10
                factors.append(f"✅ Age ({age}): Optimal age range (+10)")
            elif age < 25:
                score -= 5
                factors.append(f"⚠️ Age ({age}): Young borrower (-5)")
            else:
                score -= 10
                factors.append(f"⚠️ Age ({age}): Older borrower (-10)")
            
            # Income scoring
            if income >= 60000:
                score += 20
                factors.append(f"✅ Income (${income:,}): High income (+20)")
            elif income >= 40000:
                score += 10
                factors.append(f"✅ Income (${income:,}): Good income (+10)")
            else:
                score -= 10
                factors.append(f"❌ Income (${income:,}): Low income (-10)")
            
            # Employment stability
            if employment_length >= 5:
                score += 15
                factors.append(f"✅ Employment ({employment_length} yrs): Very stable (+15)")
            elif employment_length >= 2:
                score += 8
                factors.append(f"✅ Employment ({employment_length} yrs): Stable (+8)")
            else:
                score -= 15
                factors.append(f"❌ Employment ({employment_length} yrs): Unstable (-15)")
            
            # Loan-to-income ratio
            loan_ratio = loan_amount / income
            if loan_ratio <= 0.2:
                score += 15
                factors.append(f"✅ Loan Ratio ({loan_ratio:.1%}): Low risk (+15)")
            elif loan_ratio <= 0.4:
                score += 5
                factors.append(f"✅ Loan Ratio ({loan_ratio:.1%}): Moderate (+5)")
            else:
                score -= 20
                factors.append(f"❌ Loan Ratio ({loan_ratio:.1%}): High risk (-20)")
            
            # Credit history
            if credit_history >= 10:
                score += 15
                factors.append(f"✅ Credit History ({credit_history} yrs): Excellent (+15)")
            elif credit_history >= 5:
                score += 8
                factors.append(f"✅ Credit History ({credit_history} yrs): Good (+8)")
            else:
                score -= 5
                factors.append(f"⚠️ Credit History ({credit_history} yrs): Limited (-5)")
            
            # Home ownership
            home_scores = {'OWN': 15, 'MORTGAGE': 10, 'RENT': 0, 'OTHER': -5}
            home_score = home_scores.get(home_ownership, 0)
            score += home_score
            factors.append(f"{'✅' if home_score > 0 else '❌' if home_score < 0 else '⚠️'} Home: {home_ownership} ({home_score:+d})")
            
            # Loan grade
            grade_scores = {'A': 25, 'B': 15, 'C': 5, 'D': -5, 'E': -15, 'F': -25, 'G': -35}
            grade_score = grade_scores.get(loan_grade, 0)
            score += grade_score
            factors.append(f"{'✅' if grade_score > 0 else '❌' if grade_score < 0 else '⚠️'} Grade {loan_grade}: ({grade_score:+d})")
            
            # Loan purpose
            intent_scores = {'EDUCATION': 10, 'HOMEIMPROVEMENT': 5, 'PERSONAL': 0, 'MEDICAL': 0, 'VENTURE': -5, 'DEBTCONSOLIDATION': -15}
            intent_score = intent_scores.get(loan_intent, 0)
            score += intent_score
            factors.append(f"{'✅' if intent_score > 0 else '❌' if intent_score < 0 else '⚠️'} Purpose: {loan_intent} ({intent_score:+d})")
            
            # Default history (CRITICAL)
            if default_history == 'Y':
                score -= 40
                factors.append("❌ Previous Default: Major red flag (-40)")
            else:
                score += 15
                factors.append("✅ No Default History: Clean record (+15)")
            
            # Final decision
            approved = score >= 70
            prediction = "APPROVED" if approved else "REJECTED"
            
            explanation = f"""
**Final Score: {score}/100**
**Decision: {'✅ LOAN APPROVED' if approved else '❌ LOAN REJECTED'}**

**Scoring Breakdown:**
{chr(10).join(factors)}

{'**Congratulations!** Your loan application has been approved. You demonstrate strong creditworthiness and low default risk.' if approved else '**Unfortunately,** your application has been rejected. Focus on improving the negative factors above and reapply in 6 months.'}
            """
            
            return prediction, explanation.strip()
            
        except Exception as e:
            return "REJECTED", f"Error in prediction: {str(e)}"
    
    def serve_results(self, prediction, explanation, form_data):
        """Serve results page"""
        
        status_color = "#d4edda" if prediction == "APPROVED" else "#f8d7da"
        text_color = "#155724" if prediction == "APPROVED" else "#721c24"
        
        results_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loan Decision - {prediction}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .result-container {{ background: white; border-radius: 15px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); margin: 20px auto; max-width: 900px; }}
        .result-header {{ background: {status_color}; color: {text_color}; padding: 30px; text-align: center; border-radius: 15px 15px 0 0; }}
        .result-body {{ padding: 30px; }}
        .explanation {{ background: #f8f9fa; padding: 20px; border-radius: 10px; white-space: pre-line; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="result-container">
            <div class="result-header">
                <h1>{'🎉' if prediction == 'APPROVED' else '❌'} {prediction}</h1>
                <p>Loan Application Decision</p>
            </div>
            <div class="result-body">
                <div class="explanation">
{explanation}
                </div>
                <div class="text-center mt-4">
                    <a href="/" class="btn btn-primary">🔄 New Application</a>
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
    
    try:
        with socketserver.TCPServer(("localhost", PORT), FastCreditRiskHandler) as httpd:
            print(f"🚀 Fast Credit Risk Server running at http://localhost:{PORT}")
            print("⚡ Optimized for quick loading!")
            print("🔄 Press Ctrl+C to stop")
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            print("❌ Port 3000 is busy. Trying port 3001...")
            PORT = 3001
            with socketserver.TCPServer(("localhost", PORT), FastCreditRiskHandler) as httpd:
                print(f"🚀 Server running at http://localhost:{PORT}")
                httpd.serve_forever()
        else:
            raise e
    except KeyboardInterrupt:
        print("\\n⏹️ Server stopped")

if __name__ == "__main__":
    main()