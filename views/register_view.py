import customtkinter as ctk
from PIL import Image
from api_client import ApiClient
from gradiente_button import create_rounded_gradient_button_image

class RegisterView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F0FFF4")
        
        self.controller = controller
        self.api_client = ApiClient()

        self.header_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0, border_width=0, height=60)
        self.header_frame.place(relx=0, rely=0, relwidth=1)

        try:
            logo_header_pil = Image.open("assets/logo_header.png")
            logo_header_image = ctk.CTkImage(logo_header_pil, size=(180, 36))
            self.logo_header_label = ctk.CTkLabel(self.header_frame, image=logo_header_image, text="")
            self.logo_header_label.place(relx=0.02, rely=0.5, anchor="w")
        except FileNotFoundError:
            print("Aviso: 'assets/logo_header.png' não encontrado.")

        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")


        # Parâmetros
        WIDGET_WIDTH = 300
        WIDGET_HEIGHT = 50
        GRADIENT_PATH = "assets/gradiente.png"
        FONT_PATH = "assets/Poppins-Bold.ttf"
        
        register_title_label = ctk.CTkLabel(self.center_frame, text="Crie sua Conta",
                                            font=("Poppins", 32, "bold"), text_color="#63a87a")
        register_title_label.pack(pady=(0, 20))


        self.name_entry = ctk.CTkEntry(self.center_frame, placeholder_text="Nome Completo",
                                        width=WIDGET_WIDTH, height=WIDGET_HEIGHT, corner_radius=10,
                                        fg_color="#F7FAFC", border_color="#9edeb3", border_width=2,
                                        text_color="#305741")
        self.name_entry.pack(pady=10)

        self.email_entry = ctk.CTkEntry(self.center_frame, placeholder_text="E-mail",
                                        width=WIDGET_WIDTH, height=WIDGET_HEIGHT, corner_radius=10,
                                        fg_color="#F7FAFC", border_color="#9edeb3", border_width=2,
                                        text_color="#305741")
        self.email_entry.pack(pady=10)

        register_image = create_rounded_gradient_button_image(
            text="Cadastrar",
            width=WIDGET_WIDTH,
            height=WIDGET_HEIGHT,
            gradient_image_path=GRADIENT_PATH,
            font_path=FONT_PATH,
            font_size=18,
            corner_radius=15
        )

        if register_image:
            self.register_button = ctk.CTkButton(self.center_frame, image=register_image, text="",
                                                command=self.register_event, width=WIDGET_WIDTH, height=WIDGET_HEIGHT,
                                                fg_color="transparent", hover=False, corner_radius=15)
            self.register_button.pack(pady=10)

        self.back_button = ctk.CTkButton(self.center_frame, text="Já tem uma conta? Voltar para o Login",
                                        command=lambda: controller.show_frame("login"),
                                        fg_color="transparent", text_color="#566573",
                                        hover_color="#D4F4DE", font=("Poppins", 14))
        self.back_button.pack(pady=20)

        self.message_label = ctk.CTkLabel(self.center_frame, text="", font=("Poppins", 12))
        self.message_label.pack(pady=5)

    def register_event(self):
        """Lida com o evento de clique do botão de cadastro."""
        nome = self.name_entry.get()
        email = self.email_entry.get()

        if not nome or not email:
            self.message_label.configure(text="Nome e e-mail são obrigatórios.", text_color="#E74C3C")
            return

        # Prepara os dados para enviar à API
        user_data = {
            "nome": nome,
            "email": email
        }

        response = self.api_client.create_user(user_data)

        # Lida com a resposta da API
        if response:
            self.message_label.configure(text="Cadastro realizado com sucesso! Redirecionando...", text_color="#2ECC71")
            self.controller.after(2000, lambda: self.controller.show_frame("login"))
        else:
            self.message_label.configure(text="Erro ao cadastrar. O e-mail já pode existir.", text_color="#E74C3C")