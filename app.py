from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Database configuration
os.makedirs(app.instance_path, exist_ok=True)
db_path = os.path.join(app.instance_path, "task_manager.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =============================================
# TASK MODEL
# =============================================
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='todo')  # todo, in_progress, done
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.String(10), nullable=True)  # Format: YYYY-MM-DD

    def to_dict(self):
        """Convert task to dictionary for JSON response"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'due_date': self.due_date
        }

# =============================================
# VALIDATION HELPERS
# =============================================
def validate_status(status):
    """Validate status value"""
    valid_statuses = ['todo', 'in_progress', 'done']
    if status and status not in valid_statuses:
        return False
    return True

def validate_date_format(date_str):
    """Validate date format YYYY-MM-DD"""
    if not date_str:
        return True
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# =============================================
# REST API ENDPOINTS
# =============================================

# Create Task
@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        # Validate required field
        if not data or 'title' not in data or not data['title']:
            return jsonify({'error': 'Title is required'}), 400
        
        # Validate status
        status = data.get('status', 'todo')
        if not validate_status(status):
            return jsonify({'error': 'Invalid status. Must be: todo, in_progress, or done'}), 400
        
        # Validate due_date format
        due_date = (data.get('due_date') or "").strip() or None
        if due_date and not validate_date_format(due_date):
            return jsonify({'error': 'Invalid due_date format. Use YYYY-MM-DD'}), 400

        
        # Create new task
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            status=status,
            due_date=due_date
        )

        
        db.session.add(task)
        db.session.commit()
        
        app.logger.info(f"Task created: {task.id} - {task.title}")
        
        return jsonify(task.to_dict()), 201
        
    except Exception as e:
        app.logger.error(f"Error creating task: {str(e)}")
        return jsonify({'error': 'Failed to create task'}), 500


# List Tasks - GET /api/tasks
@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    """Get all tasks with optional filtering and sorting"""
    try:
        query = Task.query
        
        # Filter by status
        status_filter = request.args.get('status')
        if status_filter:
            if not validate_status(status_filter):
                return jsonify({'error': 'Invalid status filter'}), 400
            query = query.filter_by(status=status_filter)
        
        # Search in title and description
        search_query = request.args.get('q')
        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.filter(
                db.or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern)
                )
            )
        
        # Sorting
        sort_by = request.args.get('sort', 'created_at')
        sort_order = request.args.get('order', 'desc')  # asc or desc
        
        # Validate sort_order
        if sort_order not in ['asc', 'desc']:
            return jsonify({'error': 'Invalid order parameter. Use: asc or desc'}), 400
        
        if sort_by == 'due_date':
            # Sort by due_date
            if sort_order == 'asc':
                query = query.order_by(Task.due_date.asc().nullslast(), Task.created_at.asc())
            else:
                query = query.order_by(Task.due_date.desc().nullslast(), Task.created_at.desc())
        elif sort_by == 'created_at':
            # Sort by created_at
            if sort_order == 'asc':
                query = query.order_by(Task.created_at.asc())
            else:
                query = query.order_by(Task.created_at.desc())
        else:
            return jsonify({'error': 'Invalid sort parameter. Use: created_at or due_date'}), 400
        
        tasks = query.all()
        
        app.logger.info(f"Listed {len(tasks)} tasks")
        
        return jsonify([task.to_dict() for task in tasks]), 200
        
    except Exception as e:
        app.logger.error(f"Error listing tasks: {str(e)}")
        return jsonify({'error': 'Failed to retrieve tasks'}), 500



# Get Single Task - GET /api/tasks/<id>
@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a single task by ID"""
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': f'Task with id {task_id} not found'}), 404
        
        app.logger.info(f"Retrieved task: {task_id}")
        
        return jsonify(task.to_dict()), 200
        
    except Exception as e:
        app.logger.error(f"Error getting task: {str(e)}")
        return jsonify({'error': 'Failed to retrieve task'}), 500


# Update Task - PUT /api/tasks/<id>
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': f'Task with id {task_id} not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update title
        if 'title' in data:
            if not data['title']:
                return jsonify({'error': 'Title cannot be empty'}), 400
            task.title = data['title']
        
        # Update description
        if 'description' in data:
            task.description = data['description']
        
        # Update status
        if 'status' in data:
            if not validate_status(data['status']):
                return jsonify({'error': 'Invalid status. Must be: todo, in_progress, or done'}), 400
            task.status = data['status']
        
        # Update due_date
        if 'due_date' in data:
            new_due = (data.get('due_date') or "").strip() or None

            if new_due and not validate_date_format(new_due):
                return jsonify({'error': 'Invalid due_date format. Use YYYY-MM-DD'}), 400

            task.due_date = new_due

        
        db.session.commit()
        
        app.logger.info(f"Task updated: {task_id}")
        
        return jsonify(task.to_dict()), 200
        
    except Exception as e:
        app.logger.error(f"Error updating task: {str(e)}")
        return jsonify({'error': 'Failed to update task'}), 500


# Delete Task - DELETE /api/tasks/<id>
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task_api(task_id):
    """Delete a task"""
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': f'Task with id {task_id} not found'}), 404
        
        db.session.delete(task)
        db.session.commit()
        
        app.logger.info(f"Task deleted: {task_id}")
        
        return jsonify({'message': f'Task {task_id} deleted successfully'}), 200
        
    except Exception as e:
        app.logger.error(f"Error deleting task: {str(e)}")
        return jsonify({'error': 'Failed to delete task'}), 500

@app.route('/tasks/<int:task_id>/set_status', methods=['POST'])
def set_status(task_id):
    """Set task status to todo / in_progress / done"""
    try:
        task = Task.query.get_or_404(task_id)

        new_status = request.form.get('new_status', '').strip()

        if not validate_status(new_status):
            return "Invalid status", 400

        task.status = new_status
        db.session.commit()

        status_filter = request.form.get('status', 'all')
        return redirect(url_for('tasks_page', status=status_filter))

    except Exception as e:
        app.logger.error(f"Error setting task status: {str(e)}")
        return "Error updating task", 500



# =============================================
# FRONTEND ROUTES (HTML Pages)
# =============================================

# Home Page - GET /
@app.route('/')
def home():
    """Home page with simple intro"""
    return render_template('home.html')


# Tasks Page - GET /tasks
@app.route('/tasks')
@app.route('/tasks')
def tasks_page():
    try:
        # Filters
        status_filter = request.args.get('status', 'all')

        # Sorting
        sort_by = request.args.get('sort_by', 'created_at')  # created_at | due_date
        sort_order = request.args.get('order', 'desc')       # asc | desc

        # Counts (always from ALL tasks)
        counts = {
            "todo": Task.query.filter_by(status="todo").count(),
            "in_progress": Task.query.filter_by(status="in_progress").count(),
            "done": Task.query.filter_by(status="done").count(),
            "total": Task.query.count()
        }

        query = Task.query

        # Status filter
        if status_filter in ['todo', 'in_progress', 'done']:
            query = query.filter_by(status=status_filter)

        # Sorting
        if sort_by == 'due_date':
            column = Task.due_date
        else:
            column = Task.created_at

        if sort_order == 'asc':
            query = query.order_by(column.asc().nullslast())
        else:
            query = query.order_by(column.desc().nullslast())

        tasks = query.all()

        return render_template(
            'tasks.html',
            tasks=tasks,
            status=status_filter,
            sort_by=sort_by,
            order=sort_order,
            counts=counts
        )

    except Exception as e:
        app.logger.error(f"Error displaying tasks: {str(e)}")
        return "Error loading tasks", 500


# Mark Task as Done
@app.route('/tasks/<int:task_id>/mark_done', methods=['POST'])
def mark_done(task_id):
    """Mark a task as done"""
    try:
        task = Task.query.get_or_404(task_id)
        task.status = 'done'
        db.session.commit()
        
        status_filter = request.form.get('status', 'all')
        return redirect(url_for('tasks_page', status=status_filter))
        
    except Exception as e:
        app.logger.error(f"Error marking task as done: {str(e)}")
        return "Error updating task", 500


# Reset Task to To-Do
@app.route('/tasks/<int:task_id>/reset', methods=['POST'])
def reset_to_todo(task_id):
    """Reset a task back to todo status"""
    try:
        task = Task.query.get_or_404(task_id)
        task.status = 'todo'
        db.session.commit()
        
        status_filter = request.form.get('status', 'all')
        return redirect(url_for('tasks_page', status=status_filter))
        
    except Exception as e:
        app.logger.error(f"Error resetting task: {str(e)}")
        return "Error updating task", 500


# Delete Task (Frontend)
@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task_frontend(task_id):
    """Delete a task from frontend"""
    try:
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        
        status_filter = request.form.get('status', 'all')
        return redirect(url_for('tasks_page', status=status_filter))
        
    except Exception as e:
        app.logger.error(f"Error deleting task: {str(e)}")
        return "Error deleting task", 500


# =============================================
# ERROR HANDLERS
# =============================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint not found'}), 404
    return "Page not found", 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return "Internal server error", 500


# =============================================
# MAIN
# =============================================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created")
    
    app.run(debug=True, port=5000)