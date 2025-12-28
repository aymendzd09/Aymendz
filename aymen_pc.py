import os
from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'aymen_strong_key'

# إعداد قاعدة البيانات
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'castle.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# موديل المنشورات
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

# تصميم الصفحة الرئيسية
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏰 قلعة أيمن</title>
    <style>
        body { background: #0f0f0f; color: #e0e0e0; font-family: 'Segoe UI', Tahoma; padding: 20px; }
        .container { max-width: 600px; margin: auto; }
        h1 { color: #bb86fc; text-shadow: 2px 2px #000; border-bottom: 2px solid #bb86fc; padding-bottom: 10px; }
        .post { background: #1e1e1e; padding: 20px; margin: 20px 0; border-radius: 15px; border-left: 5px solid #03dac6; box-shadow: 0 5px 15px rgba(0,0,0,0.3); font-size: 1.2rem; }
        .footer { margin-top: 50px; font-size: 0.8rem; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏰 قلعة أيمن</h1>
        {% for post in posts %}
            <div class="post">{{ post.content }}</div>
        {% else %}
            <p>لا توجد منشورات حالياً في القلعة...</p>
        {% endfor %}
        <div class="footer">حقوق الملكية محفوظة لأيمن © 2025</div>
    </div>
</body>
</html>
'''

# تصميم لوحة التحكم
ADMIN_HTML = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <style>
        body { background: #121212; color: white; text-align: center; font-family: Arial; }
        .box { background: #1e1e1e; padding: 30px; border-radius: 10px; display: inline-block; margin-top: 50px; }
        textarea { width: 90%; height: 100px; border-radius: 5px; padding: 10px; }
        .btn { padding: 10px 20px; background: #bb86fc; border: none; border-radius: 5px; cursor: pointer; color: black; font-weight: bold; }
        .delete-btn { color: #cf6679; text-decoration: none; margin-right: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        {% if not logged_in %}
            <h2>أدخل كود القلعة</h2>
            <form method="post">
                <input type="password" name="code" placeholder="الرمز السري">
                <button type="submit" class="btn">دخول</button>
            </form>
        {% else %}
            <h2>مرحباً أيمن! 🛡️</h2>
            <form method="post">
                <textarea name="content" placeholder="ماذا تريد أن تنشر في قلعتك؟"></textarea><br><br>
                <button type="submit" class="btn">نشر الآن</button>
            </form>
            <hr>
            <h3>إدارة المنشورات:</h3>
            {% for post in posts %}
                <p>{{ post.content[:30] }}... <a href="/delete/{{ post.id }}" class="delete-btn">[حذف]</a></p>
            {% endfor %}
            <br><a href="/" style="color: #03dac6;">معاينة القلعة</a>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template_string(INDEX_HTML, posts=posts)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if 'code' in request.form:
            if request.form.get('code') == '19541962':
                session['admin'] = True
        elif session.get('admin'):
            new_post = Post(content=request.form.get('content'))
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('admin'))
    
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template_string(ADMIN_HTML, logged_in=session.get('admin'), posts=posts)

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('admin'):
        post = Post.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
