import customtkinter as ctk
from PIL import Image
from api_client import ApiClient
from gradiente_button import create_rounded_gradient_button_image
from views.login_view import LoginView
from views.register_view import RegisterView
from views.dashboard_view import DashboardView
from views.admin_view import AdminView
from views.tasks_view import TasksView
from views.checkin_view import CheckinView
from views.calendar_view import CalendarView

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MoodTasker")
        self.geometry("1200x750")
        try:
            self.iconbitmap("assets/logo.ico")
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")

        self.api_client = ApiClient()
        self.current_user = None
        self.all_tasks = []
        self.all_agendas = []
        self.all_inactive_days = []
        self.all_historicos = []
        
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.pages = {
            "login": LoginView, "register": RegisterView, "dashboard": DashboardView,
            "admin": AdminView, "tasks": TasksView, "checkin": CheckinView,
            "calendar": CalendarView
        }
        self.frames = {}

        self.show_frame("login")

    def show_frame(self, page_key):
        page_class = self.pages.get(page_key)
        if not page_class:
            print(f"Erro: Página '{page_key}' não encontrada.")
            return

        if page_key not in self.frames:
            frame = page_class(self.container, self) 
            self.frames[page_key] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        frame = self.frames[page_key]
        frame.tkraise()
                
        if hasattr(frame, 'refresh_data'):
            frame.refresh_data()

    def refresh_app_data(self, force_refresh_view=None):
        """Busca todos os dados principais da API e os armazena centralmente."""
        if not self.current_user:
            return
        
        self.all_tasks = self.api_client.get_all_tasks() or []
        self.all_agendas = self.api_client.get_all_agendas() or []
        self.all_inactive_days = self.api_client.get_dias_inativos() or []

        # Lógica para permitir forçar o refresh de uma view específica
        if force_refresh_view and force_refresh_view in self.frames:
            print(f"Forçando atualização da view: {force_refresh_view}")
            self.frames[force_refresh_view].refresh_data()
        else:
            self.update_current_frame()

    def update_current_frame(self):
        """Encontra a tela visível e chama seu método refresh_data, se ele existir."""
        for frame in self.frames.values():
            if frame.winfo_ismapped():
                if hasattr(frame, 'refresh_data'):
                    frame.refresh_data()
                    break 

    def login_success(self, user_data):
        self.current_user = user_data
        self.refresh_app_data()
        self.show_frame("dashboard")

    def login_admin_success(self, admin_data):
        self.current_user = admin_data
        self.refresh_app_data()
        self.show_frame("admin")

    def logout(self):
        self.current_user = None
        self.all_tasks, self.all_agendas, self.all_inactive_days, self.all_historicos = [], [], [], []
        self.show_frame("login") 

    def add_or_update_inactive_day(self, date_str, reason, inactive_day_id=None):
        """Cria ou atualiza um dia inativo e atualiza a aplicação."""
        if not self.current_user:
            return False

        payload = {"motivo": reason}
        response = None

        if inactive_day_id:
            response = self.api_client.update_dia_inativo(inactive_day_id, payload)
        else:
            payload["usuario_id"] = self.current_user["id"]
            payload["data"] = date_str
            response = self.api_client.create_dia_inativo(payload)
        
        if response:
            print("Operação bem-sucedida! Recarregando todos os dados...")
            self.refresh_app_data(force_refresh_view="calendar") 
            return True
        return False

    def delete_inactive_day(self, inactive_day_id):
        """Deleta um dia inativo e atualiza a aplicação."""
        if not inactive_day_id:
            return False
            
        success = self.api_client.delete_dia_inativo(inactive_day_id)
        
        if success:
            print("Deleção bem-sucedida! Recarregando todos os dados...")
            self.refresh_app_data(force_refresh_view="calendar")
            return True
        return False

    def setup_navigation_menu(self, nav_frame):
        nav_frame.grid_rowconfigure(6, weight=1)
        try:
            logo_pil = Image.open("assets/logo_header.png")
            logo_img = ctk.CTkImage(logo_pil, size=(180, 36))
            logo_label = ctk.CTkLabel(nav_frame, image=logo_img, text="")
            logo_label.pack(pady=20, padx=20)
        except FileNotFoundError:
            ctk.CTkLabel(nav_frame, text="MoodTasker", font=("Poppins", 20, "bold")).pack(pady=20, padx=20)
        
        BTN_WIDTH, BTN_HEIGHT, FONT_SIZE = 180, 40, 14
        GRADIENT_PATH, FONT_PATH, CORNER_RADIUS = "assets/gradiente.png", "assets/Poppins-Bold.ttf", 10

        button_info = {
            "Dashboard": "dashboard", "Tarefas": "tasks", 
            "Check-in Diário": "checkin", "Calendário": "calendar"
        }
        for btn_text, page_key in button_info.items():
            nav_image = create_rounded_gradient_button_image(btn_text, BTN_WIDTH, BTN_HEIGHT, GRADIENT_PATH, FONT_PATH, FONT_SIZE, CORNER_RADIUS)
            button = ctk.CTkButton(nav_frame, image=nav_image, text="", 
                                        command=lambda p=page_key: self.show_frame(p), 
                                        fg_color="transparent", hover=False, border_width=0)
            button.pack(pady=5, padx=20, fill="x")

        logout_button = ctk.CTkButton(nav_frame, text="Log out", command=self.logout, height=40, fg_color="#E74C3C", hover_color="#C0392B")
        logout_button.pack(side="bottom", pady=20, padx=20, fill="x")

if __name__ == "__main__":
    app = App()
    app.mainloop()