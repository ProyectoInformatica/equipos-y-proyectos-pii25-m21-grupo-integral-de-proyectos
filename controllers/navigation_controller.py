class NavigationController:
    def __init__(self, page, container, views):
        self.page = page
        self.container = container
        self.views = views

    def go(self, view_name):
        """Carga la vista en el contenedor."""
        self.container.content = self.views[view_name]
        self.page.update()
