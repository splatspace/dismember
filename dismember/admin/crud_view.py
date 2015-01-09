from string import capitalize

from dismember.service import db
from flask import render_template, request, flash, redirect, url_for
from wtforms import SubmitField


def configure_crud_view(blueprint, name, item_cls, new_item_form_cls, edit_item_form_cls, item_type_singular='Item',
                        item_type_plural='Items', list_order_by=None):
    """
    Configures a simple create/read/update/delete (CRUD) view for a SQLAlchemy model item.

    :param blueprint: the blueprint to attach the views to
    :param name: the name of the item to use in the blueprint to host the views.  If the blueprint's name is
        "admin" and this parameter is "users", the resulting view's URLs will end like ".../admin/users/new",
        ".../admin/users/123/delete", etc.
    :param item_cls: the SQLAlchemy model class being created/read/updated/deleted
    :param new_item_form_cls: the WTForms-Alchemy form class to show when creating a new item
    :param edit_item_form_cls: the WTForms-Alchemy form class to show when reading and updating a new item
    :param item_type_singular: a string used in the UI when a single item is described ('user', 'car', 'ox')
    :param item_type_plural: a string used in the UI when multiple items are described ('users', 'cars', 'oxen')
    :param list_order_by: a SQLAlchemy order_by clause to apply when listing items
    """

    if '.' in name:
        raise ValueError('Item name cannot contain a period')

    # Compute the endpoint names for this item so they can be used inside templates to link
    # to other CRUD endpoints and for redirection.
    pfx = '%s.%s_' % (blueprint.name, name)
    endpoints = dict(
        list_endpoint=pfx + 'list',
        create_endpoint=pfx + 'create',
        new_endpoint=pfx + 'new',
        view_endpoint=pfx + 'view',
        update_endpoint=pfx + 'update',
        delete_endpoint=pfx + 'delete',
    )

    # Also useful inside of templates.
    item_types = dict(
        item_type_singular=item_type_singular,
        item_type_plural=item_type_plural
    )

    template_kwargs = dict()
    template_kwargs.update(endpoints)
    template_kwargs.update(item_types)

    class DynamicEditItemForm(edit_item_form_cls):
        btn_save = SubmitField('Save')
        btn_cancel = SubmitField('Cancel')
        btn_delete = SubmitField('Delete')

    class DynamicNewItemForm(new_item_form_cls):
        btn_save = SubmitField('Save')
        btn_cancel = SubmitField('Cancel')

    def remove_empty_password_fields(form):
        """Removes empty password fields from the form so those fields will not be updated in the model."""
        for field in form:
            if field.type == 'PasswordField' and field.data == '':
                del form[field.name]

    def list_items():
        """Renders a list of all items."""
        q = item_cls.query
        if list_order_by:
            q = q.order_by(list_order_by)
        items = q.all()
        return render_template('admin/items/list.html',
                               items=items,
                               **template_kwargs)

    def view_item(item_id):
        """Renders a form that lets users view and edit item data."""
        item = item_cls.query.get_or_404(item_id)
        form = DynamicEditItemForm(obj=item)
        return render_template('admin/items/view.html',
                               form=form,
                               item=item,
                               item_name=str(item),
                               **template_kwargs)

    def update_item(item_id):
        """Processes the view item form data and updates an existing item."""
        item = item_cls.query.get_or_404(item_id)
        form = DynamicEditItemForm(request.form, obj=item)
        if form.validate():
            remove_empty_password_fields(form)
            form.populate_obj(item)
            db.session.add(item)
            db.session.commit()
            flash('%s "%s" updated' % (capitalize(item_type_singular), str(item)))
            return redirect(url_for(endpoints['view_endpoint'], item_id=item_id))
        return render_template('admin/items/view.html',
                               form=form,
                               item=item,
                               item_name=str(item),
                               **template_kwargs)

    def create_item():
        """Processes the new item form data and creates an item."""
        item = item_cls()
        form = DynamicNewItemForm(request.form, obj=item)
        if form.validate():
            remove_empty_password_fields(form)
            form.populate_obj(item)
            db.session.add(item)
            db.session.commit()
            flash('%s "%s" created' % (capitalize(item_type_singular), str(item)))
            return redirect(url_for(endpoints['list_endpoint']))
        return render_template('admin/items/new.html',
                               form=form,
                               item=None,
                               **template_kwargs)

    def new_item():
        """Renders the new item form."""
        # No obj arg enables smart defaults
        form = DynamicNewItemForm()
        return render_template('admin/items/new.html',
                               form=form,
                               item=None,
                               **template_kwargs)

    def delete_item(item_id):
        item = item_cls.query.get_or_404(item_id)
        item_str = str(item)
        db.session.delete(item)
        db.session.commit()
        flash('%s "%s" deleted' % (capitalize(item_type_singular), item_str))
        return 'ok', 200

    def short_endpoint(endpoint_name_key):
        """
        Get the part of the endpoint after the blueprint name (for registering URL rules
        inside a blueprint).
        """
        return endpoints[endpoint_name_key].split('.', 2)[-1]

    blueprint.add_url_rule('/%s' % name, short_endpoint('list_endpoint'),
                           view_func=list_items, methods=['GET'], strict_slashes=False)
    blueprint.add_url_rule('/%s/new' % name, short_endpoint('new_endpoint'),
                           view_func=new_item, methods=['GET'])
    blueprint.add_url_rule('/%s/new' % name, short_endpoint('create_endpoint'),
                           view_func=create_item, methods=['POST'])
    blueprint.add_url_rule('/%s/<int:item_id>' % name, short_endpoint('view_endpoint'),
                           view_func=view_item, methods=['GET'])
    blueprint.add_url_rule('/%s/<int:item_id>' % name, short_endpoint('update_endpoint'),
                           view_func=update_item, methods=['POST'])
    blueprint.add_url_rule('/%s/<int:item_id>' % name, short_endpoint('delete_endpoint'),
                           view_func=delete_item, methods=['DELETE'])

