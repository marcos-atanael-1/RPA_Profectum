from pywinauto import Application
import time

# Conecta a uma janela pelo título
app = Application().connect(title_re=".*rpa*")  # usa regex parcial
janela = app.top_window()

# Restaura e traz para frente
janela.restore()
janela.set_focus()
#janela.set_foreground()
time.sleep(1)
