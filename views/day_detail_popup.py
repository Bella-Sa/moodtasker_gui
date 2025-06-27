import customtkinter as ctk
from api_client import ApiClient
from tkinter import messagebox

class DayDetailPopup(ctk.CTkToplevel):
    def __init__(self, master, controller, selected_date, tasks_on_date, on_close_callback):
        super().__init__(master)
        
        self.transient(master)
        self.title(f"Detalhes de {selected_date.strftime('%d/%m/%Y')}")
        self.geometry("450x500")
        self.configure(fg_color="#F0FFF4")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.controller = controller
        self.api_client = ApiClient()
        self.on_close_callback = on_close_callback
        self.selected_date_str = selected_date.strftime("%Y-%m-%d")

        self.inactive_day_id = None 

        # Seção de Dia Inativo
        inactive_frame = ctk.CTkFrame(self, fg_color="#F8F9F9", corner_radius=10)
        inactive_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        inactive_frame.grid_columnconfigure(0, weight=1)

        self.inactive_var = ctk.StringVar(value="off")
        self.inactive_switch = ctk.CTkSwitch(inactive_frame, text="Marcar como dia inativo",
                                                variable=self.inactive_var, onvalue="on", offvalue="off",
                                                command=self.toggle_inactive_section)
        self.inactive_switch.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=10)

        self.motivo_label = ctk.CTkLabel(inactive_frame, text="Motivo (mín. 5 caracteres):")
        self.motivo_entry = ctk.CTkEntry(inactive_frame, placeholder_text="Ex: Feriado, Viagem...")
        self.save_inactive_button = ctk.CTkButton(inactive_frame, text="Salvar", command=self.save_inactive_day)

        # Lista de Tarefas
        tasks_list_frame = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=10)
        tasks_list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        if not tasks_on_date:
            ctk.CTkLabel(tasks_list_frame, text="Nenhuma tarefa agendada para este dia.").pack(pady=20)
        else:
            for task in tasks_on_date:
                ctk.CTkLabel(tasks_list_frame, text=f"● {task.get('titulo', 'Tarefa sem título')}", anchor="w").pack(fill="x", padx=10, pady=5)

        self.load_inactive_status() # Chama isso para configurar o switch e o campo de motivo
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Chama o callback ao fechar a janela do popup."""
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

    def toggle_inactive_section(self):
        if self.inactive_var.get() == "on":
            self.motivo_label.grid(row=1, column=0, sticky="w", padx=15, pady=(5,0))
            self.motivo_entry.grid(row=2, column=0, sticky="ew", padx=15)
            self.save_inactive_button.grid(row=3, column=0, sticky="ew", padx=15, pady=10)
        else: # Switch está sendo desativado
            self.motivo_label.grid_forget()
            self.motivo_entry.grid_forget()
            self.save_inactive_button.grid_forget()
            
            # Se havia um dia inativo salvo, pergunta se quer deletar
            if self.inactive_day_id:
                if messagebox.askyesno("Confirmar Exclusão", "Deseja remover este dia inativo?"):
                    delete_success = self.api_client.delete_dia_inativo(self.inactive_day_id)
                    if delete_success:
                        messagebox.showinfo("Sucesso", "Dia inativo removido!")
                        self.inactive_day_id = None # Reseta o ID após a exclusão
                    else:
                        messagebox.showerror("Erro", "Falha ao remover o dia inativo. O dia pode não ter sido removido.")
                        self.inactive_var.set("on") # Reativa o switch se a exclusão falhar
                else:
                    self.inactive_var.set("on") # Reativa o switch se o usuário cancelar
            # Se não havia dia inativo salvo, apenas desativou o switch, não precisa de ação na API
            # Nenhuma ação extra é necessária aqui para o refresh_app_data, pois não houve mudança de estado persistente.
            # O on_closing() será chamado quando o usuário fechar o popup, garantindo o refresh.


    def load_inactive_status(self):
        user_id = self.controller.current_user.get("id")
        self.inactive_day_id = None
        for day in self.controller.all_inactive_days:
            if day.get("usuario_id") == user_id and day.get("data") == self.selected_date_str:
                self.inactive_day_id = day.get("id")
                self.motivo_entry.delete(0, "end")
                self.motivo_entry.insert(0, day.get("motivo", ""))
                self.inactive_var.set("on") # Ativa o switch
                break
        self.toggle_inactive_section() # Garante que os campos de motivo apareçam se o switch estiver "on"
            
    def save_inactive_day(self):
        user_id = self.controller.current_user.get("id")
        motivo = self.motivo_entry.get()
        if not motivo or len(motivo) < 5:
            messagebox.showerror("Erro", "O motivo é obrigatório e precisa de no mínimo 5 caracteres.")
            return
            
        data = {"usuario_id": user_id, "data": self.selected_date_str, "motivo": motivo}
        
        response = None
        if self.inactive_day_id: # Se já existe um ID, significa que estamos atualizando (deletar e criar)
            delete_success = self.api_client.delete_dia_inativo(self.inactive_day_id)
            if delete_success:
                response = self.api_client.create_dia_inativo(data)
                if response:
                    messagebox.showinfo("Sucesso", "Dia inativo atualizado!")
                else:
                    messagebox.showerror("Erro", "Falha ao recriar dia inativo após exclusão.")
            else:
                messagebox.showerror("Erro", "Falha ao excluir o dia inativo existente para atualização.")
                return # Interrompe a função se a exclusão falhar
        else: # Se não existe ID, estamos criando um novo dia inativo
            response = self.api_client.create_dia_inativo(data)
            if response:
                messagebox.showinfo("Sucesso", "Dia inativo criado!")
            else:
                messagebox.showerror("Erro", "Não foi possível criar o dia inativo.")

        if response:
            self.on_close_callback()
            self.destroy()
        else:
            messagebox.showerror("Erro", "Não foi possível salvar o dia inativo.")