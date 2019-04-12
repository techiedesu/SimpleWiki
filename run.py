from flask import Flask,redirect,render_template,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
import re

# includes
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.jinja_env.autoescape = False
app.url_map.strict_slashes = False
db = SQLAlchemy(app)

# model
class Page(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    addr = db.Column(db.String)
    title = db.Column(db.String)
    body = db.Column(db.String)
    def __init__(self, addr, title, body):
        self.addr = addr
        self.title = title
        self.body = body
    def __repr__(self):
        return "<Page('%s','%s', '%s')>" % (self.addr, self.title, self.body)

# routes
@app.route('/')
@app.route('/wiki/')
@app.route('/wiki/<page_addr>')
def get_page(page_addr = 'index'):
    current_page = get_page_by_addr(page_addr)
    if current_page is None:
        return redirect("/wiki/%s/edit" % page_addr)
    return render_template('show.html', title = current_page.title, body = current_page.body, original_link = page_addr)

@app.route('/wiki/<page_addr>/edit', methods=['GET'])
def edit_page(page_addr):
    current_page = get_page_by_addr(page_addr)
    if current_page is None:
        page_title = ""
        page_body = ""
    else:
        page_title = current_page.title
        page_body = current_page.body

    return render_template('edit.html', title = page_title, body = page_body, original_link = page_addr)

@app.route('/wiki/<page_addr>/edit', methods=['POST'])
def edit_page_post(page_addr):
    current_page = Page.query.filter_by(addr = page_addr)

    if current_page.count() != 0:
        db.session.execute(update(Page).where(Page.addr == page_addr).values(title=request.form['title'], body=request.form['body']))
        db.session.commit()
    else:
        x = Page(page_addr, request.form['title'], request.form['body'])
        db.session.add(x)
        db.session.commit()
    return redirect("/wiki/%s/edit" % page_addr)

@app.route('/wiki/<page_addr>/delete', methods=['GET'])
def delete_page(page_addr):
    current_page = Page.query.filter_by(addr = page_addr)
    if current_page.count() != 0:
        db.session.delete(current_page.first())
        db.session.commit()
    return redirect("/wiki/index")

# ajax
@app.route('/api/exist', methods=['GET'])
def is_page_exist():
    page = request.args.get('page')
    m = re.search('^/wiki/([A-z].*)', page)
    if m:
        found = m.group(1)
        if found[-1] == '\\':
            found = found[-1]
        if get_page_by_addr(found) is not None:
            return 'true'
    return 'false'

# helpers
def get_page_by_addr(addr):
    x = Page.query.filter_by(addr = addr)
    if x.count() == 0:
        return None
    else:
        print(x.count())
        return x.first()

# >>> #
db.create_all()
index_page = Page('index', 'Главная страница', """Lorem Ipsum - это текст-"рыба", часто используемый в печати и вэб-дизайне. Lorem Ipsum является стандартной "рыбой" для текстов на латинице с начала XVI века. В то время некий безымянный печатник создал большую коллекцию размеров и форм шрифтов, используя Lorem Ipsum для распечатки образцов. Lorem Ipsum не только успешно пережил без заметных изменений пять веков, но и перешагнул в электронный дизайн. Его популяризации в новое время послужили публикация листов Letraset с образцами Lorem Ipsum в 60-х годах и, в более недавнее время, программы электронной вёрстки типа Aldus PageMaker, в шаблонах которых используется Lorem Ipsum. <a href="/wiki/page2" class="wiki-link">Страница 2</a>""")
db.session.add(index_page)
db.session.commit()

# run!
# app.run()
