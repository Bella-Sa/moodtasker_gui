import customtkinter as ctk
from PIL import Image
from api_client import ApiClient
from tkinter import messagebox
from gradiente_button import create_rounded_gradient_button_image

class TaskFormPopup(ctk.CTkToplevel):
    def __init__(self, master, controller, on_save_callback, task_data=None):
        super().__init__(master)
        
        self.transient(master)
        self.controller = controller
        self.on_save_callback = on_save_callback
        self.task_data = task_data
        self.api_client = ApiClient()
        
        self.title("Nova Tarefa" if not task_data else "Editar Tarefa")
        self.geometry("450x650")
        self.configure(fg_color="#F0FFF4")
        self.grid_columnconfigure(0, weight=1)

        self.PRIORITY_MAP = { 1: "Muito Baixa", 2: "Baixa", 3: "Média", 4: "Alta", 5: "Muito Alta" }
        LABEL_COLOR = "#305741"
        ENTRY_BG_COLOR = "#F7FAFC"
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(padx=25, pady=(20, 10), fill="x")
        try:
            logo_pil = Image.open("assets/logo.png")
            logo_img = ctk.CTkImage(logo_pil, size=(25, 25))
            logo_label = ctk.CTkLabel(header_frame, image=logo_img, text="")
            logo_label.pack(side="left")
        except FileNotFoundError:
            print("Aviso: 'assets/logo.png' não encontrado.")
        ctk.CTkLabel(header_frame, text=" Nova Tarefa" if not task_data else " Editar Tarefa", font=("Poppins", 20, "bold"), text_color=LABEL_COLOR).pack(side="left", padx=10)

        # Formulário
        ctk.CTkLabel(self, text="Título *", font=("Poppins", 14), text_color=LABEL_COLOR).pack(padx=25, pady=(10, 5), anchor="w")
        self.title_entry = ctk.CTkEntry(self, height=40, fg_color=ENTRY_BG_COLOR, border_width=1, border_color="#E0E0E0", text_color="#305741")
        self.title_entry.pack(padx=25, fill="x")

        ctk.CTkLabel(self, text="Descrição", font=("Poppins", 14), text_color=LABEL_COLOR).pack(padx=25, pady=(10, 5), anchor="w")
        self.desc_textbox = ctk.CTkTextbox(self, height=100, fg_color=ENTRY_BG_COLOR, border_width=1, border_color="#E0E0E0", text_color="#305741")
        self.desc_textbox.pack(padx=25, fill="x")

        ctk.CTkLabel(self, text="Tipo de Esforço", font=("Poppins", 14), text_color=LABEL_COLOR).pack(padx=25, pady=(10, 5), anchor="w")
        self.effort_combo = ctk.CTkComboBox(self, values=["leve", "moderado", "intenso"], height=40, state="readonly", fg_color=ENTRY_BG_COLOR, border_width=1, border_color="#E0E0E0", text_color="#305741")
        self.effort_combo.pack(padx=25, fill="x")

        priority_frame = ctk.CTkFrame(self, fg_color="transparent")
        priority_frame.pack(fill="x", padx=25, pady=(10, 5))
        ctk.CTkLabel(priority_frame, text="Prioridade:", font=("Poppins", 14), text_color=LABEL_COLOR).pack(side="left")
        self.priority_value_label = ctk.CTkLabel(priority_frame, text="", font=("Poppins", 14, "bold"), text_color=LABEL_COLOR)
        self.priority_value_label.pack(side="left", padx=5)
        
        self.priority_slider = ctk.CTkSlider(self, from_=1, to=5, number_of_steps=4, command=self.update_priority_label, progress_color="#566573", button_color="#305741")
        self.priority_slider.pack(padx=25, fill="x")
        
        time_frame = ctk.CTkFrame(self, fg_color="transparent")
        time_frame.pack(fill="x", padx=25, pady=(10, 5))
        ctk.CTkLabel(time_frame, text="Tempo Estimado:", font=("Poppins", 14), text_color=LABEL_COLOR).pack(side="left")
        self.time_value_label = ctk.CTkLabel(time_frame, text="", font=("Poppins", 14, "bold"), text_color=LABEL_COLOR)
        self.time_value_label.pack(side="left", padx=5)

        self.time_slider = ctk.CTkSlider(self, from_=5, to=240, command=self.update_time_label, progress_color="#566573", button_color="#305741")
        self.time_slider.pack(padx=25, fill="x")

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=25, pady=30)
        button_frame.grid_columnconfigure((0, 1), weight=1)

        self.cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, height=50, fg_color="#E74C3C", text_color="white", hover_color="#C0392B", corner_radius=15)
        self.cancel_button.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        save_image = create_rounded_gradient_button_image("Criar Tarefa" if not task_data else "Salvar", 200, 50, "assets/gradiente.png", "assets/Poppins-Bold.ttf", 16, 15)
        self.save_button = ctk.CTkButton(button_frame, image=save_image, text="", command=self.save_task, height=50, fg_color="transparent", hover=False)
        self.save_button.grid(row=0, column=1, sticky="ew", padx=(10, 0))

        self.set_initial_values()

    def update_priority_label(self, value):
        priority_value = int(value)
        priority_text = self.PRIORITY_MAP.get(priority_value, "Média")
        self.priority_value_label.configure(text=f"{priority_text} ({priority_value})")

    def update_time_label(self, value):
        self.time_value_label.configure(text=f"{int(value)} minutos")
        
    def set_initial_values(self):
        if self.task_data:
            self.title_entry.insert(0, self.task_data.get("titulo", ""))
            self.desc_textbox.insert("1.0", self.task_data.get("descricao", ""))
            self.effort_combo.set(self.task_data.get("tipo_esforco", "leve"))
            
            priority_val = self.task_data.get("prioridade", 3)
            self.priority_slider.set(priority_val)
            self.update_priority_label(priority_val)

            time_val = self.task_data.get("tempo_estimado", 30)
            self.time_slider.set(time_val)
            self.update_time_label(time_val)
        else:
            self.effort_combo.set("moderado")
            self.update_priority_label(self.priority_slider.get())
            self.update_time_label(self.time_slider.get())

    def save_task(self):
        if not self.title_entry.get():
            messagebox.showerror("Erro de Validação", "O título da tarefa é obrigatório.")
            return

        new_data = {
            "titulo": self.title_entry.get(),
            "descricao": self.desc_textbox.get("1.0", "end-1c"),
            "tipo_esforco": self.effort_combo.get(),
            "prioridade": int(self.priority_slider.get()),
            "tempo_estimado": int(self.time_slider.get()),
            "usuario_id": self.controller.current_user.get("id")
        }

        if self.task_data:
            self.api_client.update_task(self.task_data["id"], new_data)
        else:
            self.api_client.create_task(new_data)
        
        self.on_save_callback()
        self.destroy()
