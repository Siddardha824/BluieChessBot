from themes.bluie_theme import BluieTheme


class ThemeManager:
    def __init__(self):
        self.active_theme = BluieTheme()

    def get_theme(self):
        return self.active_theme