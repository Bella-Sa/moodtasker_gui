import customtkinter as ctk
from tkinter import messagebox

class DayDetailPopup(ctk.CTkToplevel):
    def __init__(self, master, controller, selected_date, tasks_on_date):
        super().__init__(master)
        
        self.transient(master)
        self.title(f"Detalhes de {selected_date.strftime('%d/%m/%Y')}")
        self.geometry("450x500")
        self.configure(fg_color="#F0FFF4")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.controller = controller
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

        self.load_inactive_status()

    def toggle_inactive_section(self):
        if self.inactive_var.get() == "on":
            self.motivo_label.grid(row=1, column=0, sticky="w", padx=15, pady=(5,0))
            self.motivo_entry.grid(row=2, column=0, sticky="ew", padx=15)
            self.save_inactive_button.grid(row=3, column=0, sticky="ew", padx=15, pady=10)
        else: 
            self.motivo_label.grid_forget()
            self.motivo_entry.grid_forget()
            self.save_inactive_button.grid_forget()
            
            if self.inactive_day_id:
                if messagebox.askyesno("Confirmar Exclusão", "Deseja remover este dia inativo?"):
                    success = self.controller.delete_inactive_day(self.inactive_day_id)
                    if success:
                        messagebox.showinfo("Sucesso", "Dia inativo removido!")
                        self.destroy()
                    else:
                        messagebox.showerror("Erro", "Falha ao remover o dia inativo.")
                        self.inactive_var.set("on")
                else:
                    self.inactive_var.set("on")

    def load_inactive_status(self):
        user_id = self.controller.current_user.get("id")
        self.inactive_day_id = None
        for day in self.controller.all_inactive_days:
            if day.get("usuario_id") == user_id and day.get("data") == self.selected_date_str:
                self.inactive_day_id = day.get("id")
                self.motivo_entry.delete(0, "end")
                self.motivo_entry.insert(0, day.get("motivo", ""))
                self.inactive_var.set("on")
                break
        self.toggle_inactive_section()
            
    def save_inactive_day(self):
        motivo = self.motivo_entry.get()
        if not motivo or len(motivo) < 5:
            messagebox.showerror("Erro", "O motivo é obrigatório e precisa de no mínimo 5 caracteres.")
            return
            
        success = self.controller.add_or_update_inactive_day(
            self.selected_date_str, 
            motivo, 
            self.inactive_day_id
        )

        if success:
            messagebox.showinfo("Sucesso", "Dia inativo salvo!")
            self.destroy()
        else:
            messagebox.showerror("Erro", "Não foi possível salvar o dia inativo.")