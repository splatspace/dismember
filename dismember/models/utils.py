def to_dict(o, property_names, include_none_values=False):
    """
    Get a dictionary that contains a property for each named property on the specified
    object.  Good for converting model objects to dictionaries to be sent (as JSON) to
    web services.

    :param o: the object whose properties will be read from
    :param property_names: the property names to copy
    :param include_none_values: if True values that are None will be included in the returned dictionary,
        if False only values that are not None are included
    :return: a dictionary containing the copied values
    """
    d = {}
    for name in property_names:
        if hasattr(o, name):
            v = getattr(o, name, None)
            if include_none_values or v is not None:
                d[name] = v
    return d