def allowed_overrun(func):
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return None
    return _wrapper