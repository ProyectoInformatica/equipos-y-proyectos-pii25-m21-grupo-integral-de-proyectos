class NavigationController:
    def __init__(self, page, container, views):
        self.page = page
        self.container = container
        self.views = views

    def go(self, view_name):
        """Carga la vista en el contenedor asegurando limpiar la anterior."""
        
        # Eliminar el hilo de la vista actual (si existe y tiene bucle infinito)
        if hasattr(self, 'current_view') and hasattr(self.current_view, 'matar_hilos'):
            try:
                self.current_view.matar_hilos()
            except Exception:
                pass
                
        view_item = self.views[view_name]
        # Lazy loading: si es un callable (lambda), instanciarlo ahora
        if callable(view_item):
            view = view_item()
        else:
            view = view_item
            
        self.current_view = view
        self.container.content = view
        
        # Si la vista tiene método refresh o cargar_peticiones, llamarlo para actualizar datos
        if hasattr(view, 'cargar_peticiones'):
            try:
                view.cargar_peticiones()
            except:
                pass
        elif hasattr(view, 'refresh'):
            try:
                view.refresh()
            except:
                pass
        
        self.page.update()
