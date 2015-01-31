class DetailsMixin(object):
    @property
    def details(self):
        """
        Get an iterable of string details about this model to display to users with full rights to the object.
        None if there are no details.
        """
        return None
