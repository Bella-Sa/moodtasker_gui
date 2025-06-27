import customtkinter as ctk
from api_client import ApiClient
from views.task_form_popup import TaskFormPopup
from views.feedback_popup import FeedbackPopup 
from tkinter import messagebox

class TasksView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F0FFF4")
        
        self.controller = controller
        self.api_client = ApiClient()

        # Paleta de cores para as tags
        self.PRIORITY_COLORS = { 1: {"bg": "#D5F5E3", "text": "#1D8348"}, 2: {"bg": "#FCF3CF", "text": "#F39C12"}, 3: {"bg": "#FDEBD0", "text": "#E67E22"}, 4: {"bg": "#FADBD8", "text": "#C0392B"}, 5: {"bg": "#EBDEF0", "text": "#8E44AD"} }
        self.EFFORT_COLORS = { "leve": {"bg": "#D5F5E3", "text": "#1D8348"}, "moderado":{"bg": "#FCF3CF", "text": "#F39C12"}, "intenso": {"bg": "#FADBD8", "text": "#C0392B"} }

        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Menu Lateral
        self.nav_frame = ctk.CTkFrame(self, fg_color="white", width=220, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nsw")
        self.controller.setup_navigation_menu(self.nav_frame)

        # Conteúdo Principal
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_rowconfigure(2, weight=1)

        header_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header_frame, text="Suas Tarefas", font=("Poppins", 24, "bold"), text_color="#305741").pack(side="left")
        ctk.CTkButton(header_frame, text="+ Nova Tarefa", command=self.open_task_form).pack(side="right")
        
        # Barra de Progresso
        progress_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        progress_frame.grid(row=1, column=0, sticky="ew", pady=(10, 5))
        self.progress_label = ctk.CTkLabel(progress_frame, text="Progresso Geral: 0%", font=("Poppins", 15), text_color="#305741")
        self.progress_label.pack(anchor="w")
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", expand=True, pady=2)

        # Container para a lista de tarefas
        self.tasks_list_container = ctk.CTkScrollableFrame(main_content, fg_color="white", corner_radius=10, border_width=1, border_color="#EAECEE")
        self.tasks_list_container.grid(row=2, column=0, sticky="nsew", pady=(10,0))

    def create_task_card(self, parent_frame, task, is_pending):
        card_fg_color = "#FFFFFF" if is_pending else "#F0F3F4"
        card = ctk.CTkFrame(parent_frame, fg_color=card_fg_color, border_color="#EAECEE", border_width=1, corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)

        # Adiciona o card à lista de tarefas
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

        if task.get('descricao'):
            ctk.CTkLabel(card, text=task.get('descricao'), wraplength=400, justify="left", text_color="#566573").pack(anchor="w", padx=15, pady=5)

        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(fill="x", padx=15, pady=10)
        
        if is_pending:
            ctk.CTkButton(actions_frame, text="Completar", fg_color="#65C08B", hover_color="#28B463", text_color="#F8F8F8", width=100, command=lambda t=task: self.open_feedback_form(t)).pack(side="left")
        else:
            ctk.CTkLabel(actions_frame, text="✓ Concluída", text_color="#2ECC71", font=("Poppins", 12, "bold")).pack(side="left")

        ctk.CTkButton(actions_frame, text="Editar", width=80, command=lambda t=task: self.open_task_form(t)).pack(side="left", padx=10)
        ctk.CTkButton(actions_frame, text="Deletar", text_color="#E74C3C", fg_color="transparent", hover=False, width=60, command=lambda t=task: self.delete_task(t)).pack(side="left", padx=10)

    def populate_lists(self, all_tasks):        
        """Popula a lista de tarefas com os dados recebidos do controlador."""
        for widget in self.tasks_list_container.winfo_children(): widget.destroy()

        if not self.controller.current_user: return
        user_id = self.controller.current_user.get("id")
        user_tasks = [t for t in all_tasks if t.get("usuario_id") == user_id]
        
        pending_tasks = [t for t in user_tasks if t.get("status") == "pendente"]
        completed_tasks = [t for t in user_tasks if t.get("status") != "pendente"]

        # Atualiza a barra de progresso
        if user_tasks:
            progress = len(completed_tasks) / len(user_tasks)
            self.progress_bar.set(progress)
            self.progress_label.configure(text=f"Progresso Geral: {int(progress*100)}% ({len(completed_tasks)} de {len(user_tasks)} concluídas)")
        
        if pending_tasks:
            ctk.CTkLabel(self.tasks_list_container, text="Pendentes", font=("Poppins", 18, "bold"), text_color="#305741").pack(anchor="w", padx=5, pady=(10,5))
            for task in pending_tasks: self.create_task_card(self.tasks_list_container, task, is_pending=True)
        
        if completed_tasks:
            ctk.CTkLabel(self.tasks_list_container, text="Concluídas", font=("Poppins", 18, "bold"), text_color="#305741").pack(anchor="w", padx=5, pady=(20,5))
            for task in completed_tasks: self.create_task_card(self.tasks_list_container, task, is_pending=False)

        if not pending_tasks and not completed_tasks:
            ctk.CTkLabel(self.tasks_list_container, text="Nenhuma tarefa encontrada.").pack(pady=20)


    def open_task_form(self, task_data=None):
        popup = TaskFormPopup(self, self.controller, on_save_callback=self.refresh_data, task_data=task_data)
        popup.grab_set()

    def open_feedback_form(self, task):
        popup = FeedbackPopup(self, task, on_save_callback=self.refresh_data)
        popup.grab_set()

    def delete_task(self, task):
        task_id = task.get('id')
        task_title = task.get('titulo', 'a tarefa selecionada')
        answer = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja deletar a tarefa '{task_title}'?\nEsta ação não pode ser desfeita."
        )
        if answer:
            self.api_client.delete_task(task_id)
            self.refresh_data()

    def refresh_data(self):
        """O método que o controlador principal chama para atualizar esta tela."""
        all_tasks = self.api_client.get_all_tasks()
        if all_tasks is not None:
            self.populate_lists(all_tasks)