import customtkinter as ctk
#from PIL import Image
from api_client import ApiClient
from gradiente_button import create_rounded_gradient_button_image
from tkinter import messagebox

class FeedbackPopup(ctk.CTkToplevel):
    def __init__(self, master, task_data, on_save_callback):
        super().__init__(master)
        
        self.transient(master)
        self.title("Feedback da Tarefa")
        self.geometry("450x700")
        self.configure(fg_color="#F0FFF4")
        self.grid_columnconfigure(0, weight=1)

        self.api_client = ApiClient()
        self.task_data = task_data
        self.on_save_callback = on_save_callback
        
        self.satisfaction_var = ctk.IntVar(value=3)
        self.classification_var = ctk.StringVar(value="Neutra")
        self.post_task_energy_var = ctk.DoubleVar(value=50)

        # --- Paleta de Cores ---
        self.CLASSIFICATION_COLORS = {
            "Motivadora": "#1D8348",   
            "Neutra": "#F39C12",       
            "Desgastante": "#C0392B"   
        }
        

        ctk.CTkLabel(self, text="Como foi essa tarefa?", font=("Poppins", 22, "bold"), text_color="#305741").pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Seu feedback nos ajuda a entender como as tarefas afetam seu bem-estar.", wraplength=380, text_color="#566573").pack(pady=(0, 20))

        ctk.CTkLabel(self, text="Qual seu nível de satisfação com esta tarefa?", font=("Poppins", 14, "bold"), text_color="#305741").pack(pady=(10, 5))
        satisfaction_frame = ctk.CTkFrame(self, fg_color="transparent")
        satisfaction_frame.pack(pady=10)
        for i in range(1, 6):
            btn = ctk.CTkButton(satisfaction_frame, text=f"{i}", width=50, command=lambda v=i: self.satisfaction_var.set(v))
            btn.pack(side="left", padx=5)

        ctk.CTkLabel(self, text="Como esta tarefa afetou seu estado emocional?", font=("Poppins", 14, "bold"), text_color="#305741").pack(pady=(20, 5))
        self.create_classification_option("Motivadora", "Esta tarefa me deu energia e motivação", "#D5F5E3")
        self.create_classification_option("Neutra", "Esta tarefa não afetou significativamente meu humor", "#FCF3CF")
        self.create_classification_option("Desgastante", "Esta tarefa me cansou ou causou estresse", "#FADBD8")
        
        energy_title_frame = ctk.CTkFrame(self, fg_color="transparent")
        energy_title_frame.pack(fill="x", padx=25, pady=(15, 5))
        ctk.CTkLabel(energy_title_frame, text="Qual seu nível de energia após a tarefa?", font=("Poppins", 14, "bold"), text_color="#305741").pack(side="left")
        
        self.post_task_energy_label = ctk.CTkLabel(energy_title_frame, text="", font=("Poppins", 14, "bold"), text_color="#305741")
        self.post_task_energy_label.pack(side="left", padx=5)

        self.energy_slider = ctk.CTkSlider(self, from_=0, to=100, variable=self.post_task_energy_var, 
                                            fg_color="#D3D3D3", progress_color="#566573", 
                                            command=self.update_post_task_energy_label)
        self.energy_slider.pack(fill="x", padx=25, pady=5)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=25, pady=(30, 20))
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.skip_button = ctk.CTkButton(button_frame, text="Pular Feedback", command=self.skip_feedback, height=50, fg_color="#F2F3F4", text_color="#566573", hover_color="#E5E7E9", corner_radius=15)
        self.skip_button.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        submit_image = create_rounded_gradient_button_image("Enviar Feedback", 200, 50, "assets/gradiente.png", "assets/Poppins-Bold.ttf", 16, 15)
        self.submit_button = ctk.CTkButton(button_frame, image=submit_image, text="", command=self.send_feedback, height=50, fg_color="transparent", hover=False)
        self.submit_button.grid(row=0, column=1, sticky="ew", padx=(10, 0))

        self.update_post_task_energy_label(self.post_task_energy_var.get())

    def create_classification_option(self, title, subtitle, bg_color):
        option_frame = ctk.CTkFrame(self, fg_color=bg_color, corner_radius=10, border_width=1, border_color="#DDDDDD")
        option_frame.pack(fill="x", padx=25, pady=5)
        
        radio_button = ctk.CTkRadioButton(option_frame, text="", variable=self.classification_var, value=title)
        radio_button.pack(side="left", padx=(15,10))
        
        text_frame = ctk.CTkFrame(option_frame, fg_color="transparent")
        text_frame.pack(side="left", padx=(0,15), pady=10, fill="x")
        
        text_color = self.CLASSIFICATION_COLORS.get(title, "#305741")
        ctk.CTkLabel(text_frame, text=title, font=("Poppins", 14, "bold"), text_color=text_color, anchor="w").pack(fill="x")
        ctk.CTkLabel(text_frame, text=subtitle, text_color="#566573", anchor="w").pack(fill="x")
    
    def update_post_task_energy_label(self, value):
        """Atualiza o texto do label com o valor atual do slider de energia."""
        self.post_task_energy_label.configure(text=f"({int(value)})")

    def send_feedback(self):
        feedback_data = {
            "status": "completo",
            "nivel_satisfacao_pos_tarefa": self.satisfaction_var.get(),
            "classificacao_pos_tarefa": self.classification_var.get().lower(),
            "energia_pos_tarefa": int(self.post_task_energy_var.get())
        }
        task_update_success = self.api_client.update_task(self.task_data['id'], feedback_data)
        
        user_id = self.task_data['usuario_id']
        user_energy_data = { "energia": int(self.post_task_energy_var.get()) }
        user_update_success = self.api_client.update_user_checkin(user_id, user_energy_data)
        
        if task_update_success and user_update_success:
            messagebox.showinfo("Sucesso", "Tarefa finalizada e feedback enviado com sucesso!")
            if self.on_save_callback:
                self.on_save_callback()
            self.destroy()
        else:
            messagebox.showerror("Erro", "Falha ao enviar feedback ou atualizar usuário.")

    def skip_feedback(self):
        task_update_success = self.api_client.update_task(self.task_data['id'], {"status": "completo"})
        if task_update_success:
            ctk.CTkMessagebox.showinfo("Sucesso", "Tarefa marcada como completa (feedback pulado).")
            if self.on_save_callback:
                self.on_save_callback()
            self.destroy()
        else:
            messagebox.showerror("Erro", "Falha ao marcar tarefa como completa.")   