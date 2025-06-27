import customtkinter as ctk
from api_client import ApiClient
from views.task_form_popup import TaskFormPopup
from views.feedback_popup import FeedbackPopup
from tkinter import messagebox

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F0FFF4")
        
        self.controller = controller
        self.api_client = ApiClient()

        # Paleta de Cores Dinâmicas
        
        self.MOOD_COLORS = {
            "Terrível": "#E74C3C", 
            "Ruim": "#9B59B6",      
            "Neutro(a)": "#F1C40F", 
            "Bom/Boa": "#3498DB",   
            "Ótimo(a)": "#2ECC71"    
        }
        self.PRIORITY_COLORS = {
            1: {"bg": "#D5F5E3", "text": "#1D8348"},  
            2: {"bg": "#FCF3CF", "text": "#F39C12"},  
            3: {"bg": "#FDEBD0", "text": "#D4690C"},  
            4: {"bg": "#FADBD8", "text": "#8E44AD"},  
            5: {"bg": "#EBDEF0", "text": "#C0392B"}  
        }
        self.EFFORT_COLORS = {
            "leve":    {"bg": "#D5F5E3", "text": "#1D8348"},  
            "moderado":{"bg": "#FCF3CF", "text": "#F39C12"}, 
            "intenso": {"bg": "#FADBD8", "text": "#C0392B"}  
        }

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Menu Lateral
        self.nav_frame = ctk.CTkFrame(self, fg_color="white", width=220, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nsw")
        self.controller.setup_navigation_menu(self.nav_frame)

        # Conteúdo Principal
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(2, weight=1)

        self.welcome_label = ctk.CTkLabel(self.main_content, text="Bem-vindo(a)!", font=("Poppins", 24, "bold"), text_color="#305741")
        self.welcome_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        self.summary_cards_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.summary_cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.summary_cards_frame.grid_columnconfigure((0, 1), weight=1)
        self.create_summary_cards()

        self.tasks_area_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.tasks_area_frame.grid(row=2, column=0, sticky="nsew")
        self.tasks_area_frame.grid_rowconfigure(1, weight=1)
        self.tasks_area_frame.grid_columnconfigure(0, weight=1)
        
        tasks_header_frame = ctk.CTkFrame(self.tasks_area_frame, fg_color="transparent")
        tasks_header_frame.grid(row=0, column=0, sticky="ew")
        tasks_header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(tasks_header_frame, text="Suas Tarefas Pendentes", font=("Poppins", 20, "bold"), text_color="#305741").pack(side="left")
        ctk.CTkButton(tasks_header_frame, text="+ Nova Tarefa", command=self.open_task_form).pack(side="right")

        self.tasks_list_frame = ctk.CTkScrollableFrame(self.tasks_area_frame, fg_color="transparent", corner_radius=0)
        self.tasks_list_frame.grid(row=1, column=0, sticky="nsew", pady=10)

    def open_task_form(self, task_data=None):
        """Abre o pop-up para criar ou editar uma tarefa."""
        popup = TaskFormPopup(self, self.controller, on_save_callback=self.refresh_data, task_data=task_data)
        popup.grab_set()

    def create_summary_cards(self):
        self.tasks_card = ctk.CTkFrame(self.summary_cards_frame, fg_color="white", corner_radius=10, border_color="#E0E0E0", border_width=1)
        self.tasks_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.tasks_card.pack_propagate(False)
        self.tasks_card.configure(height=100)
        ctk.CTkLabel(self.tasks_card, text="Tarefas Concluídas", font=("Poppins", 14), text_color="#566573").pack(anchor="w", padx=15, pady=(10,0))
        self.tasks_count_label = ctk.CTkLabel(self.tasks_card, text="0 / 0", font=("Poppins", 28, "bold"), text_color="#305741")
        self.tasks_count_label.pack(anchor="w", padx=15)
        self.mood_card = ctk.CTkFrame(self.summary_cards_frame, fg_color="white", corner_radius=10, border_color="#E0E0E0", border_width=1)
        self.mood_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.mood_card.pack_propagate(False)
        self.mood_card.configure(height=100)
        ctk.CTkLabel(self.mood_card, text="Humor Atual", font=("Poppins", 14), text_color="#566573").pack(anchor="w", padx=15, pady=(10,0))
        self.humor_label = ctk.CTkLabel(self.mood_card, text="N/A", font=("Poppins", 22, "bold"))
        self.humor_label.pack(anchor="w", padx=15)
        self.energy_label = ctk.CTkLabel(self.mood_card, text="Energia: N/A%", font=("Poppins", 15), text_color="#566573")
        self.energy_label.pack(anchor="w", padx=15)

    def populate_task_cards(self, tasks):
        for widget in self.tasks_list_frame.winfo_children():
            widget.destroy()
        
        if not tasks:
            ctk.CTkLabel(self.tasks_list_frame, text="Nenhuma tarefa pendente! ✨").pack(pady=20)
            return

        for task in tasks:
            card = ctk.CTkFrame(self.tasks_list_frame, fg_color="white", border_color="#EAECEE", border_width=1, corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(card, text=task.get('titulo', 'Sem Título'), font=("Poppins", 16, "bold"), text_color="#305741").pack(anchor="w", padx=15, pady=(10,0))
            tags_frame = ctk.CTkFrame(card, fg_color="transparent")
            tags_frame.pack(fill="x", padx=15, pady=5)
            priority = task.get('prioridade', 1)
            effort = task.get('tipo_esforco', 'leve')
            priority_color = self.PRIORITY_COLORS.get(priority, {"bg": "#E5E7E9", "text": "#566573"})
            effort_color = self.EFFORT_COLORS.get(effort, {"bg": "#E5E7E9", "text": "#566573"})
            ctk.CTkLabel(tags_frame, text=f"Prioridade: {priority}", fg_color=priority_color["bg"], text_color=priority_color["text"], corner_radius=5).pack(side="left", padx=(0,5))
            ctk.CTkLabel(tags_frame, text=effort.capitalize(), fg_color=effort_color["bg"], text_color=effort_color["text"], corner_radius=5).pack(side="left", padx=5)
            ctk.CTkLabel(tags_frame, text=f"{task.get('tempo_estimado')} min", fg_color="#E5E7E9", text_color="#566573", corner_radius=5).pack(side="left", padx=5)
            ctk.CTkLabel(card, text=task.get('descricao', ''), wraplength=400, justify="left", text_color="#566573").pack(anchor="w", padx=15, pady=5)
            actions_frame = ctk.CTkFrame(card, fg_color="transparent")
            actions_frame.pack(fill="x", padx=15, pady=10)
            ctk.CTkButton(actions_frame, text="Completar", fg_color="#65C08B", hover_color="#28B463", text_color="#F8F8F8", width=100, command=lambda t=task: self.open_feedback_form(t)).pack(side="left")
            ctk.CTkButton(actions_frame, text="Editar", width=80, command=lambda t=task: self.open_task_form(t)).pack(side="left", padx=10)
            ctk.CTkButton(actions_frame, text="Deletar", text_color="#E74C3C", fg_color="transparent", hover=False, width=60, command=lambda t=task: self.delete_task(t)).pack(side="left", padx=10)

    def open_feedback_form(self, task):
        """Abre o pop-up para dar feedback."""
        popup = FeedbackPopup(self, task, on_save_callback=self.refresh_data)
        popup.grab_set()

    def complete_task(self, task_id):
        print(f"Marcando tarefa {task_id} como completa...")
        update_data = {"status": "completo"}
        self.api_client.update_task(task_id, update_data)
        self.refresh_data()
    
    def delete_task(self, task):

        task_title = task.get('titulo', 'a tarefa selecionada')
        answer = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja deletar a tarefa '{task_title}'?\nEsta ação não pode ser desfeita."
        )
        if answer:
            self.api_client.delete_task()
            self.refresh_data()

    def refresh_data(self):
        if not self.controller.current_user: return
        user_id = self.controller.current_user.get("id")
        user_name = self.controller.current_user.get("nome", "Usuário")
        self.welcome_label.configure(text=f"Bem-vindo(a), {user_name.split()[0]}!")
        user_data = self.api_client.get_user_by_id(user_id)
        tasks = self.api_client.get_all_tasks()
        
        humor = "N/A"
        energia = "N/A"
        if user_data:
            humor = user_data.get("humor", "-")
            energia = user_data.get("energia", "- ")
            mood_color = self.MOOD_COLORS.get(humor, "#566573")
            self.humor_label.configure(text=humor, text_color=mood_color)
            self.energy_label.configure(text=f"Energia: {energia}%")

        total_tasks, completed_count, pending_tasks = 0, 0, []
        if tasks:
            user_tasks = [t for t in tasks if t.get("usuario_id") == user_id]
            completed_count = len([t for t in user_tasks if t.get("status") == "completo"])
            total_tasks = len(user_tasks)
            pending_tasks = [t for t in user_tasks if t.get("status") == "pendente"]
        
        self.tasks_count_label.configure(text=f"{completed_count} / {total_tasks}")
        self.populate_task_cards(pending_tasks)