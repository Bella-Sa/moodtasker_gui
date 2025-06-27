import customtkinter as ctk
from tkcalendar import Calendar
from api_client import ApiClient
from views.day_detail_popup import DayDetailPopup
from datetime import datetime

class CalendarView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F0FFF4")
        
        self.controller = controller
        self.api_client = ApiClient()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.nav_frame = ctk.CTkFrame(self, fg_color="white", width=220, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nsw")
        self.controller.setup_navigation_menu(self.nav_frame)
        
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_content.grid_rowconfigure(1, weight=1)
        main_content.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(main_content, text="Calendário de Tarefas", font=("Poppins", 24, "bold"), text_color="#305741").grid(row=0, column=0, sticky="w")
        
        self.cal = Calendar(main_content, selectmode='day', locale='pt_BR',
                            background="#3498DB", foreground='white',
                            headersbackground="#2980B9", headersforeground='white',
                            normalbackground='white', weekendbackground='#F2F3F4',
                            selectbackground='#2ECC71', selectforeground='white',
                            othermonthbackground='#EAECEE', othermonthforeground='gray')
        self.cal.grid(row=1, column=0, sticky="nsew", pady=10)
        self.cal.bind("<<CalendarSelected>>", self.on_day_selected)

    def mark_events(self):
        self.cal.calevent_remove("all")
        events = {}
        
        if not self.controller.current_user: return
        user_id = self.controller.current_user.get("id")

        for agenda in self.controller.all_agendas:
            task = next((t for t in self.controller.all_tasks if t.get("id") == agenda.get("tarefa_id")), None)
            if task and task.get("usuario_id") == user_id:
                date_str = agenda.get("data")
                if date_str not in events: events[date_str] = {"tasks": 0, "inactive_reason": None}
                events[date_str]["tasks"] += 1
        
        for day in self.controller.all_inactive_days:
            if day.get("usuario_id") == user_id:
                date_str = day.get("data")
                if date_str not in events: events[date_str] = {"tasks": 0, "inactive_reason": None}
                events[date_str]["inactive_reason"] = day.get("motivo")

        for date_str, info in events.items():
            try:
                event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if info["inactive_reason"]:
                    self.cal.calevent_create(event_date, info["inactive_reason"], "inactive")
                elif info["tasks"] > 0:
                    self.cal.calevent_create(event_date, f"{info['tasks']} Tarefa(s)", "event")
            except (ValueError, TypeError):
                continue
        
        self.cal.tag_config("event", background="green", foreground="white")
        self.cal.tag_config("inactive", background="#3498DB", foreground="white")

    def on_day_selected(self, event):
        selected_date = self.cal.selection_get()
        
        tasks_on_day = []
        user_id = self.controller.current_user.get("id")
        for agenda in self.controller.all_agendas:
            if agenda.get("data") == selected_date.strftime("%Y-%m-%d"):
                task_id = agenda.get("tarefa_id")
                task_details = next((t for t in self.controller.all_tasks if t.get("id") == task_id and t.get("usuario_id") == user_id), None)
                if task_details:
                    tasks_on_day.append(task_details)

        popup = DayDetailPopup(self, self.controller, selected_date, tasks_on_day, on_close_callback=self.controller.refresh_app_data)
        popup.grab_set()

    def refresh_data(self):
        print("Atualizando a tela de Calendário com dados da memória...")
        self.mark_events()