from flask import Flask, render_template, request, redirect, url_for
from jinja2 import TemplateNotFound
import sys
import unittest

app = Flask(__name__)
todo_list = [
    {"task": "Buy Milk", "email": "antchrobiaka@gmail.com", "priority": "Medium"}
]
VALID_PRIORITIES = {"Low", "Medium", "High"}
@app.route('/')
def index():
    try:
        return render_template('index.html', todos=todo_list)
    except TemplateNotFound:
        rows = "\n".join(
            f"<tr><td>{item['task']}</td><td>{item['email']}</td><td>{item['priority']}</td></tr>"
            for item in todo_list
        )
        return f"""
        <!doctype html>
        <html>
          <head>
            <meta charset="utf-8">
            <title>To Do List (fallback)</title>
          </head>
          <body>
            <h1>To Do List (fallback)</h1>
            <table border="1" cellpadding="5">
              <tr><th>Task</th><th>Email</th><th>Priority</th></tr>
              {rows}
            </table>
            <h2>Add New Item</h2>
            <form action="/submit" method="post">
              <label>Task:</label>
              <input type="text" name="task" required><br><br>

              <label>Email:</label>
              <input type="email" name="email" required><br><br>

              <label>Priority:</label>
              <select name="priority">
                <option>Low</option>
                <option selected>Medium</option>
                <option>High</option>
              </select><br><br>

              <button type="submit">Add</button>
            </form>

            <br>
            <a href="/clear">Clear List</a>
          </body>
        </html>
        """
@app.route('/submit', methods=['POST'])
def submit():
    task = (request.form.get('task') or '').strip()
    email = (request.form.get('email') or '').strip()
    priority = (request.form.get('priority') or '').strip().title()
    if not task:
        return redirect(url_for('index'))

    if not email or '@' not in email:
        return redirect(url_for('index'))

    if priority not in VALID_PRIORITIES:
        priority = 'Low'

    todo_list.append({'task': task, 'email': email, 'priority': priority})
    return redirect(url_for('index'))
@app.route('/clear')
def clear():
    todo_list.clear()
    return redirect(url_for('index'))
class TodoAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        todo_list.clear()
        todo_list.append({"task": "Buy Milk", "email": "antchrobiaka@gmail.com", "priority": "Medium"})

    def test_index_contains_initial_item(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        body = rv.get_data(as_text=True)
        self.assertIn('Buy Milk', body)
        self.assertIn('antchrobiaka@gmail.com', body)
        self.assertIn('Medium', body)
    def test_submit_adds_item(self):
        rv = self.app.post('/submit', data={
            'task': 'Test Task',
            'email': 'tester@example.com',
            'priority': 'High'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        body = rv.get_data(as_text=True)
        self.assertIn('Test Task', body)
        self.assertIn('tester@example.com', body)
        self.assertIn('High', body)
    def test_clear_empties_list(self):
        rv = self.app.get('/clear', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        body = rv.get_data(as_text=True)
        self.assertNotIn('Buy Milk', body)
if __name__ == '__main__':
    if 'test' in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
