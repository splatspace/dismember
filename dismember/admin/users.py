from dismember.admin import admin_bp
from dismember.models.user import User
from dismember.service import db
from dismember.wtforms_alchemy.forms import SessionModelForm, TimeZoneAwareFieldMeta
from flask import url_for, request, redirect, render_template, flash


class UserForm(SessionModelForm):
    class Meta(TimeZoneAwareFieldMeta):
        model = User


class NewUserForm(UserForm):
    class Meta(UserForm.Meta):
        exclude = ['confirmed_at', 'last_login_at', 'current_login_at', 'last_login_ip', 'current_login_ip',
                   'login_count']


@admin_bp.route('/users')
def users_list():
    users = User.query.order_by(User.full_name.desc()).all()
    return render_template('list_items.html',
                           items=users,
                           title='Users',
                           new_endpoint='admin.users_new',
                           view_endpoint='admin.users_view')


@admin_bp.route('/users', methods=['POST'])
def users_create():
    user = User()
    form = UserForm(request.form)
    form.populate_obj(user)
    db.session.add(user)
    db.session.commit()
    flash('User "%s" created' % str(user))
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/users/new')
def users_new():
    form = NewUserForm()
    return render_template('new_item.html',
                           form=form,
                           item=None,
                           title='New User',
                           create_endpoint='admin.users_create')


@admin_bp.route('/users/<item_id>')
def users_view(item_id):
    user = User.query.get_or_404(item_id)
    form = UserForm(obj=user)
    return render_template('edit_item.html',
                           form=form,
                           item=user,
                           title=str(user),
                           update_endpoint='admin.users_update',
                           delete_endpoint='admin.users_delete',
                           after_delete_endpoint='admin.users_list')


@admin_bp.route('/users/<item_id>', methods=['POST'])
def users_update(item_id):
    user = User.query.get_or_404(item_id)
    form = UserForm(request.form)
    form.populate_obj(user)
    db.session.add(user)
    db.session.commit()
    flash('User "%s" updated' % str(user))
    return redirect(url_for('admin.users_update', item_id=item_id))


@admin_bp.route('/users/<item_id>/delete', methods=['DELETE'])
def users_delete(item_id):
    user = User.query.get_or_404(item_id)
    user_str = str(user)
    db.session.delete(user)
    db.session.commit()
    flash('User "%s" deleted' % user_str)
    return 'ok', 200