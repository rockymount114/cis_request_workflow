
import base64
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from docusign_service import create_and_send_envelope

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///requests.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

class UserRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    middle_initial = db.Column(db.String(1), nullable=True)
    last_name = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    division_no = db.Column(db.String(50), nullable=False)
    employee_id = db.Column(db.String(50), nullable=False)
    supervisor_name = db.Column(db.String(100), nullable=False)
    primary_work_location = db.Column(db.String(100), nullable=False)
    work_phone = db.Column(db.String(20), nullable=False)
    work_email = db.Column(db.String(120), nullable=False)
    request_type = db.Column(db.String(50), nullable=False)
    environment = db.Column(db.String(50), nullable=False)
    model_user = db.Column(db.String(100), nullable=True)
    justification = db.Column(db.Text, nullable=False)
    security_group = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Pending Department Manager Approval')

    def __repr__(self):
        return f'<UserRequest {self.first_name} {self.last_name}>'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    new_request = UserRequest(
        first_name=request.form['first_name'],
        middle_initial=request.form['middle_initial'],
        last_name=request.form['last_name'],
        job_title=request.form['job_title'],
        division_no=request.form['division_no'],
        employee_id=request.form['employee_id'],
        supervisor_name=request.form['supervisor_name'],
        primary_work_location=request.form['primary_work_location'],
        work_phone=request.form['work_phone'],
        work_email=request.form['work_email'],
        request_type=request.form['request_type'],
        environment=request.form['environment'],
        model_user=request.form['model_user'],
        justification=request.form['justification'],
        security_group=request.form['security_group']
    )
    db.session.add(new_request)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    pending_requests = UserRequest.query.filter(UserRequest.status != 'Approved').all()
    return render_template('dashboard.html', requests=pending_requests)

@app.route('/approve/<int:request_id>')
def approve(request_id):
    user_request = UserRequest.query.get_or_404(request_id)
    if user_request.status == 'Pending Department Manager Approval':
        user_request.status = 'Pending Business & Collections Services Director Approval'
    elif user_request.status == 'Pending Business & Collections Services Director Approval':
        user_request.status = 'Pending CIS Infinity Administrator Approval'
    elif user_request.status == 'Pending CIS Infinity Administrator Approval':
        user_request.status = 'Approved'
        # Trigger DocuSign when fully approved
        document_html = render_template("docusign_form.html", user_request=user_request)
        document_b64 = base64.b64encode(document_html.encode('utf-8')).decode('ascii')
        envelope_id = create_and_send_envelope(user_request, document_b64)
        if envelope_id:
            print(f"Successfully sent envelope {envelope_id} for user request {user_request.id}")
        else:
            print(f"Failed to send envelope for user request {user_request.id}")

    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/reject/<int:request_id>')
def reject(request_id):
    user_request = UserRequest.query.get_or_404(request_id)
    user_request.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

