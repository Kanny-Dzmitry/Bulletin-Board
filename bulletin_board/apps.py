from django.apps import AppConfig


class BulletinBoardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bulletin_board'
    verbose_name = 'Доска объявлений'
    
    def ready(self):
        """Импортировать сигналы при запуске приложения"""
        import bulletin_board.signals
