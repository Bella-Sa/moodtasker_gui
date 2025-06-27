import customtkinter as ctk
from api_client import ApiClient
from gradiente_button import create_rounded_gradient_button_image

class EditUserPopup(ctk.CTkToplevel):
    def __init__(self, master, user_data, on_save_callback):
        super().__init__(master)
        
        self.transient(master)
        self.title("Editar Usuário")
        self.geometry("400x550")
        self.configure(fg_color="#F0FFF4")
        self.grid_columnconfigure(0, weight=1)

        self.api_client = ApiClient()
        self.user_data = user_data
        self.on_save_callback = on_save_callback

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(padx=20, pady=20, fill="x")
        
        title_label = ctk.CTkLabel(header_frame, text="Editar Usuário", font=("Poppins", 20, "bold"), text_color="#305741")
        title_label.pack(side="left", padx=10)

        LABEL_COLOR = "#305741"
        ENTRY_BG_COLOR = "#F7FAFC"

        ctk.CTkLabel(self, text="Nome Completo", text_color=LABEL_COLOR).pack(padx=20, pady=(0, 5), anchor="w")
        self.name_entry = ctk.CTkEntry(self, height=40, fg_color=ENTRY_BG_COLOR, border_width=0, text_color="#305741")
        self.name_entry.pack(padx=20, fill="x")
        self.name_entry.insert(0, self.user_data.get("nome", ""))

        ctk.CTkLabel(self, text="E-mail", text_color=LABEL_COLOR).pack(padx=20, pady=(10, 5), anchor="w")
        self.email_entry = ctk.CTkEntry(self, height=40, fg_color=ENTRY_BG_COLOR, border_width=0, text_color="#305741")
        self.email_entry.pack(padx=20, fill="x")
        self.email_entry.insert(0, self.user_data.get("email", ""))
        
        humor_options = ["Terrível", "Ruim", "Neutro(a)", "Bom/Boa", "Ótimo(a)", ""]
        ctk.CTkLabel(self, text="Humor", text_color=LABEL_COLOR).pack(padx=20, pady=(10, 5), anchor="w")
        self.humor_combo = ctk.CTkComboBox(self, values=humor_options, height=40, state="readonly", fg_color=ENTRY_BG_COLOR, border_width=0)
        self.humor_combo.pack(padx=20, fill="x")
        self.humor_combo.set(self.user_data.get("humor") or "")

        energy_frame = ctk.CTkFrame(self, fg_color="transparent")
        energy_frame.pack(padx=20, pady=(10, 0), fill="x")
        
        ctk.CTkLabel(energy_frame, text="Nível de Energia:", text_color=LABEL_COLOR).pack(side="left")
        self.energy_value_label = ctk.CTkLabel(energy_frame, text="", text_color=LABEL_COLOR, font=("Poppins", 12, "bold"))
        self.energy_value_label.pack(side="right")

        initial_energy = self.user_data.get("energia") or 50
        self.energy_slider = ctk.CTkSlider(self, from_=0, to=100, command=self.update_energy_label,
                                            progress_color="#567359", button_color="#244832")
        self.energy_slider.pack(padx=20, fill="x", pady=5)
        self.energy_slider.set(initial_energy)
        self.update_energy_label(initial_energy)

        self.active_switch_var = ctk.StringVar(value="on" if self.user_data.get("ativo", True) else "off")
        self.active_switch = ctk.CTkSwitch(self, text="Usuário Ativo", variable=self.active_switch_var, onvalue="on", offvalue="off", text_color=LABEL_COLOR)
        self.active_switch.pack(padx=20, pady=20)

        save_image = create_rounded_gradient_button_image("Salvar Alterações", 360, 50, "assets/gradiente.png", "assets/Poppins-Bold.ttf", 16, 15)
        if save_image:
            self.save_button = ctk.CTkButton(self, image=save_image, text="", command=self.save_changes, fg_color="transparent", hover=False)
            self.save_button.pack(padx=20, pady=10, fill="x")

    def update_energy_label(self, value):
        self.energy_value_label.configure(text=f"{int(value)}")
        
    def save_changes(self):
        updated_data = {
            "nome": self.name_entry.get(),
            "email": self.email_entry.get(),
            "humor": self.humor_combo.get() or None,
            "energia": int(self.energy_slider.get()),
            "ativo": self.active_switch_var.get() == "on"
        }
        
        user_id = self.user_data.get("id")
        self.api_client.update_user(user_id, updated_data)
        self.on_save_callback()
        self.destroy()