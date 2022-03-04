

def register_addon():

    # Operators
    from ..operator import register_operators
    register_operators()
    
    from ..panels import register_panels
    register_panels()
    
    #from ..ui_lists import register_lists
    #register_lists()
    
    from ..property import register_properties
    register_properties()


def unregister_addon():

    # Operators
    from ..operator import unregister_operators
    unregister_operators()
    
    from ..panels import unregister_panels
    unregister_panels()
    
    #from ..ui_lists import unregister_lists
    #unregister_lists()
    
    from ..property import unregister_properties
    unregister_properties()

