import os
from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "aymen_dz_strong_99"

# إعداد قاعدة البيانات للحفظ الدائم
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///castle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# تعريف جدول المنشورات
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# --- واجهة الهاتف (HTML) ---
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>قلعة أيمن</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f0f0f; color: #e0e0e0; padding: 15px; margin: 0; }
        .container { max-width: 600px; margin: auto; }
        h1 { text-align: center; color: #007bff; text-shadow: 2px 2px 5px rgba(0,0,0,0.5); }
        .post { background: #1a1a1a; padding: 15px; border-radius: 12px; margin-bottom: 20px; border-right: 6px solid #007bff; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
        .post p { line-height: 1.6; font-size: 1.1em; margin: 0 0 10px 0; }
        .date { font-size: 0.75em; color: #777; border-top: 1px solid #333; pt: 5px; }
        .admin-link { text-align: center; margin-top: 30px; font-size: 0.8em; }
        .admin-link a { color: #444; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏰 قلعة أيمن</h1>
        {% for post in posts %}
        <div class="post">
            <p>{{ post.content }}</p>
            <div class="date">نُشر في: {{ post.date_posted.strftime('%Y-%m-%d %H:%M') }}</div>
        </div>
        {% else %}
        <p style="text-align:center; color:#555;">لا توجد منشورات حالياً في القلعة.</p>
        {% endfor %}
        <div class="admin-link"><a href="/admin">لوحة التحكم</a></div>
    </div>
</body>
</html>
"""

ADMIN_LAYOUT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم</title>
    <style>
        body { background: #121212; color: white; font-family: sans-serif; padding: 20px; }
        textarea { width: 100%; height: 120px; border-radius: 8px; background: #222; color: white; padding: 10px; border: 1px solid #444; }
        button { width: 100%; padding: 12px; background: #28a745; border: none; color: white; border-radius: 8px; margin-top: 10px; cursor: pointer; }
        .post-item { background: #1e1e1e; padding: 10px; margin-top: 10px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
        .del-btn { color: #ff4444; text-decoration: none; font-weight: bold; padding: 5px 10px; border: 1px solid #ff4444; border-radius: 5px; }
    </style>
</head>
<body>
    <h2>إدارة القلعة</h2>
    <form action="/add_post" method="post">
        <textarea name="content" placeholder="ماذا تريد أن تنشر يا أيمن؟" required></textarea>
        <button type="submit">نشر الآن</button>
    </form>
    <hr>
    <h3>المنشورات الحالية:</h3>
    {% for post in posts %}
    <div class="post-item">
        <span>{{ post.content[:30] }}...</span>
        <a href="/delete/{{ post.id }}" class="del-btn" onclick="return confirm('هل أنت متأكد من حذف المنشور؟')">حذف [X]</a>
    </div>
    {% endfor %}
    <br><a href="/" style="color:#007bff; text-decoration:none;">العودة للموقع</a>
</body>
</html>
"""

# --- المسارات (Routes) ---

@app.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template_string(HTML_LAYOUT, posts=posts)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '19541962': # كلمة السر تاعك
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return "كلمة سر خاطئة!"
    
    if not session.get('admin'):
        return '''
        <body style="background:#121212; color:white; text-align:center; padding-top:100px; font-family:sans-serif;">
            <form method="post">
                <h3>أدخل كود القلعة للعبور</h3>
                <input type="password" name="password" style="padding:10px; border-radius:5px;"><br><br>
                <button type="submit" style="padding:10px 20px; background:#007bff; color:white; border:none; border-radius:5px;">دخول</button>
            </form>
        </body>
        '''
    
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template_string(ADMIN_LAYOUT, posts=posts)

@app.route('/add_post', methods=['POST'])
def add_post():
    if session.get('admin'):
        content = request.form.get('content')
        if content:
            new_post = Post(content=content)
            db.session.add(new_post)
            db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('admin'):
        post = Post.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
