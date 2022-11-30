import main

class ConfigLoad():
    """
    This class creates a Window thats enables to read in config files.
    """
    def __init__(self,root):
        """
        This class initializes the configuration window for the measurement
        """
        self.root = root
        title = "Neues Fenster"
        self.root.title(title)

        self.root.mainloop()

