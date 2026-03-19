import sys

from PyQt6.QtWidgets import QApplication

from controllers import RestauranteController
from models import RestauranteModel
from views import RestauranteWindow


def main() -> None:
    app = QApplication(sys.argv)

    model = RestauranteModel()
    controller = RestauranteController(model)
    window = RestauranteWindow(controller)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
