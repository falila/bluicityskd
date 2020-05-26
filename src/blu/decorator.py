import logging

class GerenericDecorator(object):
    
    def __init__(self, scenario_id):
        self.scenario_id = scenario_id

    def operation(self,**kwargs):
        logging.info(" operaton event ...")

    def __call__(self, f):    
        def wrapped_f(*args, **kwargs):
            self.operation(**kwargs)
            f(*args, **kwargs)
        return wrapped_f


def sell_deco(arg1):
    """  """
    #TODO add config validation check
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            f(*args, **kwargs)
        return wrapped_f
    return wrap