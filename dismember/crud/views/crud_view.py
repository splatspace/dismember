from dismember.service import db
from dismember.wtforms_components.fields import remove_empty_password_fields
from flask import render_template, request, flash, redirect, url_for
from wtforms import SubmitField


class CrudView(object):
    def __init__(self, blueprint, name, item_cls, new_item_form_cls, edit_item_form_cls, item_type_singular='Item',
                 item_type_plural='Items', list_order_by=None):
        """
        Creates a simple create/read/update/delete (CRUD) view for a SQLAlchemy model item.

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
        super(CrudView, self).__init__()

        if '.' in name:
            raise ValueError('Item name cannot contain a period')

        self._name = name
        self._item_cls = item_cls
        self._list_order_by = list_order_by
        self._item_type_singular = item_type_singular
        self._item_type_plural = item_type_plural

        # Compute the endpoint names for this item so they can be used inside templates to link
        # to other CRUD endpoints and for redirection.
        pfx = '%s.%s_' % (blueprint.name, name)
        self._endpoints = dict(
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

        self.template_kwargs = dict()
        self.template_kwargs.update(self._endpoints)
        self.template_kwargs.update(item_types)

        class DynamicEditItemForm(edit_item_form_cls):
            btn_save = SubmitField('Save')
            btn_cancel = SubmitField('Cancel')
            btn_delete = SubmitField('Delete')

        self.dynamic_edit_item_form = DynamicEditItemForm

        class DynamicNewItemForm(new_item_form_cls):
            btn_save = SubmitField('Save')
            btn_cancel = SubmitField('Cancel')

        self.dynamic_new_item_form = DynamicNewItemForm

        blueprint.add_url_rule('/%s' % name, self._short_endpoint('list_endpoint'),
                               view_func=self.list_items, methods=['GET'], strict_slashes=False)
        blueprint.add_url_rule('/%s/new' % name, self._short_endpoint('new_endpoint'),
                               view_func=self.new_item, methods=['GET'])
        blueprint.add_url_rule('/%s/new' % name, self._short_endpoint('create_endpoint'),
                               view_func=self.create_item, methods=['POST'])
        blueprint.add_url_rule('/%s/<int:item_id>' % name, self._short_endpoint('view_endpoint'),
                               view_func=self.view_item, methods=['GET'])
        blueprint.add_url_rule('/%s/<int:item_id>' % name, self._short_endpoint('update_endpoint'),
                               view_func=self.update_item, methods=['POST'])
        blueprint.add_url_rule('/%s/<int:item_id>' % name, self._short_endpoint('delete_endpoint'),
                               view_func=self.delete_item, methods=['DELETE'])

    @property
    def item_type_singular(self):
        return self._item_type_singular

    @property
    def item_type_plural(self):
        return self._item_type_plural

    @property
    def endpoints(self):
        return self._endpoints

    def list_items(self):
        """Renders a list of all items."""
        q = self._item_cls.query
        if self._list_order_by:
            q = q.order_by(self._list_order_by)
        items = q.all()
        return render_template('crud/list.html',
                               items=items,
                               **self.template_kwargs)

    def view_item(self, item_id):
        """Renders a form that lets users view and edit item data."""
        item = self._item_cls.query.get_or_404(item_id)
        form = self.dynamic_edit_item_form(obj=item)
        return render_template('crud/view.html',
                               form=form,
                               item=item,
                               item_name=str(item),
                               **self.template_kwargs)

    def update_item(self, item_id):
        """Processes the view item form data and updates an existing item."""
        item = self._item_cls.query.get_or_404(item_id)
        form = self.dynamic_edit_item_form(request.form, obj=item)
        if form.validate():
            remove_empty_password_fields(form)
            form.populate_obj(item)
            db.session.add(item)
            db.session.commit()
            flash('%s "%s" updated' % (self.item_type_singular, str(item)))
            return redirect(url_for(self._endpoints['view_endpoint'], item_id=item_id))
        return render_template('crud/view.html',
                               form=form,
                               item=item,
                               item_name=str(item),
                               **self.template_kwargs)

    def create_item(self):
        """Processes the new item form data and creates an item."""
        item = self._item_cls()
        form = self.dynamic_new_item_form(request.form, obj=item)
        if form.validate():
            remove_empty_password_fields(form)
            form.populate_obj(item)
            db.session.add(item)
            db.session.commit()
            flash('%s "%s" created' % (self.item_type_singular, str(item)))
            return redirect(url_for(self._endpoints['list_endpoint']))
        return render_template('crud/new.html',
                               form=form,
                               item=None,
                               **self.template_kwargs)

    def new_item(self):
        """Renders the new item form."""
        # No obj arg enables smart defaults
        form = self.dynamic_new_item_form()
        return render_template('crud/new.html',
                               form=form,
                               item=None,
                               **self.template_kwargs)

    def delete_item(self, item_id):
        item = self._item_cls.query.get_or_404(item_id)
        item_str = str(item)
        db.session.delete(item)
        db.session.commit()
        flash('%s "%s" deleted' % (self.item_type_singular, item_str))
        return 'ok', 200

    def _short_endpoint(self, endpoint_name_key):
        """
        Get the part of the endpoint after the blueprint name (for registering URL rules
        inside a blueprint).
        """
        return self._endpoints[endpoint_name_key].split('.', 2)[-1]
