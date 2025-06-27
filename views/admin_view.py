import customtkinter as ctk
from PIL import Image
from api_client import ApiClient
from views.edit_user_popup import EditUserPopup
from tkinter import messagebox
from gradiente_button import create_rounded_gradient_button_image

class AdminView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F0FFF4")
        
        self.controller = controller
        self.api_client = ApiClient()
        self.selected_user_id = None
        self.selected_user_data = None

        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1)
        
        self.header_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0, border_width=0, height=60)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        try:
            logo_header_pil = Image.open("assets/logo_header.png")
            logo_header_image = ctk.CTkImage(logo_header_pil, size=(180, 36))
            logo_label = ctk.CTkLabel(self.header_frame, image=logo_header_image, text="")
            logo_label.place(relx=0.02, rely=0.5, anchor="w")
        except FileNotFoundError:
            print("Aviso: 'assets/logo_header.png' não encontrado.")
        
        self.page_title = ctk.CTkLabel(self, text="Dashboard Administrador", font=("Poppins", 24, "bold"), text_color="#305741")
        self.page_title.grid(row=0, column=0, pady=(70, 0), padx=20, sticky="w")

        # Container da lista
        self.user_list_container = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.user_list_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.user_list_container.grid_columnconfigure(0, weight=1)
        self.user_list_container.grid_rowconfigure(1, weight=1)

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, sticky="s", padx=20, pady=(0, 20))
        self.bottom_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.setup_buttons()
        self.setup_user_list_header()
        
        self.user_widgets = {}
        self.load_users()

    def setup_user_list_header(self):
        header = ctk.CTkFrame(self.user_list_container, fg_color="#EBF5FB", height=40, corner_radius=5)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # Uso do .grid() e configurando o peso das colunas
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=3)
        header.grid_columnconfigure(2, weight=4)
        header.grid_columnconfigure(3, weight=2)
        header.grid_columnconfigure(4, weight=1)
        header.grid_columnconfigure(5, weight=1)
        
        header_font = ("Poppins", 12, "bold")
        TEXT_COLOR = "#305741"
        
        ctk.CTkLabel(header, text="ID", font=header_font, text_color=TEXT_COLOR).grid(row=0, column=0, sticky="w", padx=10)
        ctk.CTkLabel(header, text="Nome", font=header_font, text_color=TEXT_COLOR).grid(row=0, column=1, sticky="w", padx=10)
        ctk.CTkLabel(header, text="E-mail", font=header_font, text_color=TEXT_COLOR).grid(row=0, column=2, sticky="w", padx=10)
        ctk.CTkLabel(header, text="Humor", font=header_font, text_color=TEXT_COLOR).grid(row=0, column=3, sticky="w", padx=10)
        ctk.CTkLabel(header, text="Energia", font=header_font, text_color=TEXT_COLOR).grid(row=0, column=4, sticky="w", padx=10)
        ctk.CTkLabel(header, text="Ativo", font=header_font, text_color=TEXT_COLOR).grid(row=0, column=5, sticky="w", padx=10)
        
        self.user_list_frame = ctk.CTkScrollableFrame(self.user_list_container, fg_color="white")
        self.user_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.user_list_frame.grid_columnconfigure(0, weight=1)

    def populate_user_list(self, users):
            for widget in self.user_list_frame.winfo_children():
                widget.destroy()
            self.user_widgets.clear()

            for i, user in enumerate(users):
                user_id = user['id']
                row_color = "white" if i % 2 == 0 else "#F8F9F9"
                
                user_frame = ctk.CTkFrame(self.user_list_frame, fg_color=row_color, corner_radius=0)
                user_frame.pack(fill="x")
                
                # Configuração das colunas do grid para esta linha
                user_frame.grid_columnconfigure(0, weight=1)
                user_frame.grid_columnconfigure(1, weight=3)
                user_frame.grid_columnconfigure(2, weight=4)
                user_frame.grid_columnconfigure(3, weight=2)
                user_frame.grid_columnconfigure(4, weight=1)
                user_frame.grid_columnconfigure(5, weight=1)

                row_font = ("Consolas", 12) 
                TEXT_COLOR = "#305741"

                ctk.CTkLabel(user_frame, text=user_id, font=row_font, text_color=TEXT_COLOR, justify="left").grid(row=0, column=0, sticky="w", padx=10, pady=4)
                ctk.CTkLabel(user_frame, text=user.get('nome', '-'), font=row_font, text_color=TEXT_COLOR, anchor="w", justify="left").grid(row=0, column=1, sticky="w", padx=10, pady=4)
                ctk.CTkLabel(user_frame, text=user.get('email', '-'), font=row_font, text_color=TEXT_COLOR, anchor="w", justify="left").grid(row=0, column=2, sticky="w", padx=10, pady=4)
                ctk.CTkLabel(user_frame, text=str(user.get('humor', '-')), font=row_font, text_color=TEXT_COLOR, anchor="w").grid(row=0, column=3, sticky="w", padx=10, pady=4)
                ctk.CTkLabel(user_frame, text=str(user.get('energia', '-')), font=row_font, text_color=TEXT_COLOR).grid(row=0, column=4, sticky="w", padx=10, pady=4)
                ctk.CTkLabel(user_frame, text=str(user.get('ativo', '-')), font=row_font, text_color=TEXT_COLOR).grid(row=0, column=5, sticky="w", padx=10, pady=4)
                
                self.user_widgets[user_id] = {'frame': user_frame}
                user_frame.bind("<Button-1>", lambda event, u=user: self.select_user(u))
                for child in user_frame.winfo_children():
                    child.bind("<Button-1>", lambda event, u=user: self.select_user(u))

    def setup_buttons(self):
        BTN_WIDTH, BTN_HEIGHT, FONT_SIZE = 200, 50, 16
        GRADIENT_PATH, FONT_PATH, CORNER_RADIUS = "assets/gradiente.png", "assets/Poppins-Bold.ttf", 15
        add_image = create_rounded_gradient_button_image("Adicionar Usuário", BTN_WIDTH, BTN_HEIGHT, GRADIENT_PATH, FONT_PATH, FONT_SIZE, CORNER_RADIUS)
        edit_image = create_rounded_gradient_button_image("Editar Selecionado", BTN_WIDTH, BTN_HEIGHT, GRADIENT_PATH, FONT_PATH, FONT_SIZE, CORNER_RADIUS)
        logout_image = create_rounded_gradient_button_image("Log out", BTN_WIDTH, BTN_HEIGHT, GRADIENT_PATH, FONT_PATH, FONT_SIZE, CORNER_RADIUS)
        self.add_button = ctk.CTkButton(self.bottom_frame, image=add_image, text="", command=self.add_user_popup, fg_color="transparent", hover=False, border_width=0)
        self.add_button.grid(row=0, column=0, padx=5)
        self.edit_button = ctk.CTkButton(self.bottom_frame, image=edit_image, text="", command=self.edit_user_popup, state="disabled", fg_color="transparent", hover=False, border_width=0)
        self.edit_button.grid(row=0, column=1, padx=5)
        self.delete_button = ctk.CTkButton(self.bottom_frame, text="Deletar Selecionado", width=BTN_WIDTH, height=BTN_HEIGHT, command=self.delete_user_event, state="disabled", fg_color="#E74C3C", hover_color="#C0392B", text_color="#FFFFFF", corner_radius=CORNER_RADIUS, font=(FONT_PATH.split('/')[-1].split('.')[0], FONT_SIZE, "bold"))
        self.delete_button.grid(row=0, column=2, padx=5)
        self.logout_button = ctk.CTkButton(self.bottom_frame, image=logout_image, text="", command=lambda: self.controller.logout(), fg_color="transparent", hover=False, border_width=0)
        self.logout_button.grid(row=0, column=3, padx=5)

    def load_users(self):
        self.clear_selection()
        users = self.api_client.get_all_users()
        if users:
            self.populate_user_list(users)
            
    def select_user(self, user_data):
        for i, (uid, widgets) in enumerate(self.user_widgets.items()):
            original_color = "white" if i % 2 == 0 else "#F8F9F9"
            if widgets['frame'].winfo_exists():
                widgets['frame'].configure(fg_color=original_color)
        selected_id = user_data['id']
        if selected_id in self.user_widgets:
            self.user_widgets[selected_id]['frame'].configure(fg_color="#A9DFBF")
        self.selected_user_id = selected_id
        self.selected_user_data = user_data
        self.edit_button.configure(state="normal")
        self.delete_button.configure(state="normal")

    def clear_selection(self):
        self.selected_user_id = None
        self.selected_user_data = None
        if hasattr(self, 'edit_button') and self.edit_button.winfo_exists():
            self.edit_button.configure(state="disabled")
        if hasattr(self, 'delete_button') and self.delete_button.winfo_exists():
            self.delete_button.configure(state="disabled")
        for i, (uid, widgets) in enumerate(self.user_widgets.items()):
            original_color = "white" if i % 2 == 0 else "#F8F9F9"
            if widgets['frame'].winfo_exists():
                widgets['frame'].configure(fg_color=original_color)
    
    def add_user_popup(self):
        self.controller.show_frame("register")

    def edit_user_popup(self):
        if not self.selected_user_data:
            return
        popup = EditUserPopup(self, self.selected_user_data, on_save_callback=self.load_users)
        popup.grab_set()

    def delete_user_event(self):
        if not self.selected_user_id:
            return
        answer = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja deletar o usuário '{self.selected_user_data.get('nome')}'?")
        if answer:
            self.api_client.delete_user(self.selected_user_id)
            self.load_users()

    def refresh_data(self):
        self.load_users()