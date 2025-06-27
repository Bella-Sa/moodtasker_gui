
import customtkinter as ctk
#from PIL import Image
from api_client import ApiClient
from gradiente_button import create_rounded_gradient_button_image
from datetime import date
from tkinter import messagebox

class CheckinView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F0FFF4")
        
        self.controller = controller
        self.api_client = ApiClient()

        # --- MUDANÇA: Paleta de Cores corrigida e em uso ---
        self.MOOD_COLORS = {
            "Terrível":  {"bg": "#EBDEF0", "text": "#8E44AD"}, # Roxo
            "Ruim":      {"bg": "#FADBD8", "text": "#C0392B"}, # Vermelho
            "Neutro(a)": {"bg": "#FCF3CF", "text": "#F39C12"}, # Amarelo
            "Bom/Boa":   {"bg": "#D6EAF8", "text": "#3498DB"}, # Azul
            "Ótimo(a)":  {"bg": "#D5F5E3", "text": "#1D8348"}  # Verde
        }
        
        self.mood_var = ctk.StringVar()
        self.energy_var = ctk.DoubleVar()

        # --- Estrutura da Tela ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Menu Lateral
        self.nav_frame = ctk.CTkFrame(self, fg_color="white", width=220, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nsw")
        self.controller.setup_navigation_menu(self.nav_frame)

        # Conteúdo Principal
        main_content = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        main_content.grid(row=0, column=1, sticky="nsew", padx=40, pady=20)
        main_content.grid_columnconfigure(0, weight=1)
        
        # Título
        ctk.CTkLabel(main_content, text="Registro de Humor", font=("Poppins", 24, "bold"), text_color="#305741").pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(main_content, text="Como você está se sentindo hoje?", font=("Poppins", 16), text_color="#566573").pack(anchor="w", pady=(0, 20))
        
        # Painel de Nível de Energia 
        energy_panel = ctk.CTkFrame(main_content, fg_color="transparent")
        energy_panel.pack(fill="x", expand=True, pady=10)
        ctk.CTkLabel(energy_panel, text="Nível de Energia", font=("Poppins", 18, "bold"), text_color="#305741").pack(anchor="w")
        self.energy_value_label = ctk.CTkLabel(energy_panel, text="50%", font=("Poppins", 32, "bold"), text_color="#305741")
        self.energy_value_label.pack(anchor="center", pady=10)
        self.energy_slider = ctk.CTkSlider(energy_panel, from_=0, to=100, variable=self.energy_var, command=self.update_energy_label, fg_color="#D3D3D3", progress_color="#566573")
        self.energy_slider.pack(fill="x", expand=True)

        # Painel de Estado de Humor
        mood_panel = ctk.CTkFrame(main_content, fg_color="transparent")
        mood_panel.pack(fill="x", expand=True, pady=20)
        ctk.CTkLabel(mood_panel, text="Estado de Humor", font=("Poppins", 18, "bold"), text_color="#305741").pack(anchor="w")
        
        for mood_text in self.MOOD_COLORS.keys():
            self.create_mood_option(mood_panel, mood_text)

        # Botão de Salvar
        save_image = create_rounded_gradient_button_image("Salvar Check-in", 300, 50, "assets/gradiente.png", "assets/Poppins-Bold.ttf", 16, 15)
        self.save_button = ctk.CTkButton(main_content, image=save_image, text="", command=self.save_checkin, fg_color="transparent", hover=False, border_width=0) # MUDANÇA: Removida a borda azul
        self.save_button.pack(pady=20)
        
        self.success_label = ctk.CTkLabel(main_content, text="", text_color="#2ECC71")
        self.success_label.pack(pady=10)


    def create_mood_option(self, parent_frame, mood_text):
        """Cria uma opção de humor estilizada com um RadioButton."""
        color_map = self.MOOD_COLORS.get(mood_text)
        option_frame = ctk.CTkFrame(parent_frame, fg_color=color_map["bg"], border_color="#DDDDDD", border_width=1, corner_radius=10)
        option_frame.pack(fill="x", pady=5)
        
        radio_button = ctk.CTkRadioButton(option_frame, text="", variable=self.mood_var, value=mood_text)
        radio_button.pack(side="left", padx=(15, 10))
        
        ctk.CTkLabel(option_frame, text=mood_text, font=("Poppins", 14, "bold"), text_color=color_map["text"]).pack(side="left", padx=10, pady=15)
        
    def update_energy_label(self, value):
        self.energy_value_label.configure(text=f"{int(value)}%")

    def save_checkin(self):
        user_id = self.controller.current_user.get("id")
        if not user_id: return

        checkin_data = {
            "humor": self.mood_var.get(),
            "energia": int(self.energy_var.get()),
            "data_checkin": str(date.today())
        }
        response = self.api_client.update_user_checkin(user_id, checkin_data)
        if response:
                    messagebox.showinfo("Sucesso", "Check-in diário registrado. Obrigada!")
                    
                    dashboard = self.controller.frames.get("dashboard")
                    if dashboard:
                        dashboard.refresh_data()
        else:
            messagebox.showerror("Erro", "Não foi possível salvar o check-in. Tente novamente.")
        
    def refresh_data(self):
        if not self.controller.current_user: return
        
        user_id = self.controller.current_user.get("id")
        user_data = self.api_client.get_user_by_id(user_id)

        if user_data:
            self.mood_var.set(user_data.get("humor", "Neutro(a)"))
            energy_val = user_data.get("energia", 50)
            self.energy_var.set(energy_val)
            self.update_energy_label(energy_val)