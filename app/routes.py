from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .models import Item, User, Settings
from . import db

main = Blueprint('main', __name__)

# ======== Dashboard ========
@main.route('/')
@login_required
def dashboard():
    items = Item.query.all()
    working = Item.query.filter_by(status='Çalışıyor').count()
    maintenance = Item.query.filter_by(status='Bakım Gerekli').count()
    broken = Item.query.filter_by(status='Arızalı').count()
    return render_template('dashboard.html',
                           items=items,
                           working=working,
                           maintenance=maintenance,
                           broken=broken)

# ======== Malzemeler ========
@main.route('/materials')
@login_required
def materials():
    items = Item.query.all()
    return render_template('materials.html', items=items)

@main.route('/item/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        # تحويل نص التاريخ إلى كائن date
        maintenance_str = request.form['maintenance_date']
        maintenance_date = datetime.strptime(maintenance_str, '%Y-%m-%d').date()
        status = request.form['status']
        new_item = Item(
            name=name,
            location=location,
            maintenance_date=maintenance_date,
            status=status
        )
        db.session.add(new_item)
        db.session.commit()
        flash('تم إضافة القطعة بنجاح.', 'success')
        return redirect(url_for('main.materials'))
    return render_template('yeni.html')

@main.route('/item/<int:item_id>')
@login_required
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('detail.html', item=item)

@main.route('/item/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.location = request.form['location']
        # تحويل نص التاريخ إلى كائن date
        maintenance_str = request.form['maintenance_date']
        item.maintenance_date = datetime.strptime(maintenance_str, '%Y-%m-%d').date()
        item.status = request.form['status']
        db.session.commit()
        flash('تم حفظ التعديلات بنجاح.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('edit.html', item=item)

@main.route('/item/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('تم حذف القطعة.', 'success')
    return redirect(url_for('main.dashboard'))

# ======== إدارة المستخدمين ========
@main.route('/users')
@login_required
def users():
    if current_user.role != 'Admin':
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة.', 'danger')
        return redirect(url_for('main.dashboard'))
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@main.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'Admin':
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة.', 'danger')
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        hashed = generate_password_hash(password)
        new_user = User(username=username, password=hashed, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('تم إنشاء المستخدم بنجاح.', 'success')
        return redirect(url_for('main.users'))
    return render_template('add_user.html')

@main.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'Admin':
        flash('ليس لديك صلاحية الوصول إلى هذه العملية.', 'danger')
        return redirect(url_for('main.dashboard'))
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الحالي!', 'warning')
        return redirect(url_for('main.users'))
    db.session.delete(user)
    db.session.commit()
    flash('تم حذف المستخدم.', 'success')
    return redirect(url_for('main.users'))

# ======== الإعدادات ========
@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    setting = Settings.query.first()
    if request.method == 'POST':
        # إذا كانت هناك حقول تغيير كلمة المرور
        if 'old_password' in request.form and 'new_password' in request.form:
            old = request.form['old_password']
            new = request.form['new_password']
            confirm = request.form['confirm_password']
            if new != confirm:
                flash('كلمات المرور الجديدة غير متطابقة.', 'danger')
            elif not check_password_hash(current_user.password, old):
                flash('كلمة المرور القديمة غير صحيحة.', 'danger')
            else:
                current_user.password = generate_password_hash(new)
                db.session.commit()
                flash('تم تغيير كلمة المرور بنجاح.', 'success')
        else:
            # تحديث اسم الموقع
            setting.site_name = request.form['site_name']
            db.session.commit()
            flash('تم تحديث الإعدادات العامة.', 'success')
        return redirect(url_for('main.settings'))
    return render_template('settings.html', setting=setting)

# ======== تسجيل الخروج ========
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
