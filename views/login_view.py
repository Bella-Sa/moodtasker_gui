import customtkinter as ctk
from PIL import Image
from api_client import ApiClient
from gradiente_button import create_rounded_gradient_button_image 

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F0FFF4")
        
        self.controller = controller
        self.api_client = ApiClient()

        self.header_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0, border_width=0, height=60)
        self.header_frame.place(relx=0, rely=0, relwidth=1)

        try:
            logo_header_pil = Image.open("assets/logo_header.png")
            logo_header_image = ctk.CTkImage(logo_header_pil, size=(180, 40))
            self.logo_header_label = ctk.CTkLabel(self.header_frame, image=logo_header_image, text="")
            self.logo_header_label.place(relx=0.02, rely=0.5, anchor="w")
        except FileNotFoundError:
            print("Aviso: 'assets/logo_header.png' não encontrado.")

        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        BUTTON_WIDTH = 300
        BUTTON_HEIGHT = 50
        GRADIENT_PATH = "assets/gradiente.png"
        FONT_PATH = "assets/Poppins-Bold.ttf"
        BUTTON_CORNER_RADIUS = 15

        login_title_label = ctk.CTkLabel(self.center_frame, text="Login",
                                        font=("Poppins", 40, "bold"), text_color="#63a87a")
        login_title_label.pack(pady=(0, 20))

        self.email_entry = ctk.CTkEntry(self.center_frame, placeholder_text="E-mail",
                                        width=BUTTON_WIDTH, height=BUTTON_HEIGHT, corner_radius=10,
                                        fg_color="#F7FAFC", border_color="#9edeb3", border_width=2, font=("Poppins", 14),
                                        text_color="#305741")
        self.email_entry.pack(pady=20)

        # Cria a imagem do botão gradiente dinamicamente
        login_image = create_rounded_gradient_button_image(
            text="Entrar",
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
            gradient_image_path=GRADIENT_PATH,
            font_path=FONT_PATH,
            font_size=20,
            corner_radius=BUTTON_CORNER_RADIUS
        )

        # Botão "Entrar"
        if login_image:
            self.login_button = ctk.CTkButton(self.center_frame, image=login_image, text="",
                                            command=self.login_event, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                            fg_color="transparent", hover=False, corner_radius=BUTTON_CORNER_RADIUS)
            self.login_button.pack(pady=10)

        # Botão "Cadastre-se"
        self.register_button = ctk.CTkButton(self.center_frame, text="Não tem uma conta? Cadastre-se",
                                            command=self.go_to_register,
                                            fg_color="transparent", text_color="#566573", font=("Poppins", 14),
                                            hover_color="#D4F4DE")
        self.register_button.pack(pady=20)


        self.error_label = ctk.CTkLabel(self.center_frame, text="", text_color="#E74C3C", font=("Poppins", 14))
        self.error_label.pack(pady=5)

    def go_to_register(self):
        """Chama o controlador para mostrar a tela de registro."""
        self.controller.show_frame("register")
    
    def login_event(self):
        """Lida com o evento de clique do botão de login."""
        email = self.email_entry.get()
        if not email:
            self.error_label.configure(text="Por favor, insira um e-mail.")
            return
        
        self.error_label.configure(text="")
        user = self.api_client.get_user_by_email(email)

        if user:
            if user.get('email') == 'admmoodtasker@gmail.com':
                self.controller.login_admin_success(user)
            else:
                self.controller.login_success(user)
        else:
            self.error_label.configure(text="E-mail ou senha inválidos.")