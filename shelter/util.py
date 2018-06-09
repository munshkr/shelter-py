def memoize(dicc_name):
    def decorator(func):
        def wrapper(self, key):
            dicc = getattr(self, dicc_name)
            if key in dicc:
                return dicc[key]
            else:
                value = func(self, key)
                dicc[key] = value
                return value

        return wrapper

    return decorator
