import requests

BASE_URL = "http://127.0.0.1:5000"

class ApiClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {"Content-Type": "application/json"}

    def _handle_response(self, response):
        """Função auxiliar para tratar as respostas da API."""
        try:
            if not response.content:
                return True
            return response.json()
        except Exception as e:
            print(f"Erro ao decodificar resposta JSON: {e}")
            return None

    def _request(self, method, endpoint, data=None):
        """Função auxiliar para fazer requisições."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, json=data, headers=self.headers)
            response.raise_for_status() # Lança um erro para códigos de status HTTP 4xx e 5xx
            return self._handle_response(response)
        except requests.exceptions.HTTPError as e:
            print(f"Erro HTTP: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão na API: {e}")
        return None

    # --- Métodos de Usuário ---
    def get_user_by_email(self, email):
        """Busca um usuário pelo e-mail."""
        return self._request("GET", f"/usuarios/email/{email}")
    
    def get_user_by_id(self, user_id):
        """Busca um usuário pelo seu ID."""
        return self._request("GET", f"/usuarios/{user_id}")

    def get_all_users(self):
        """Busca todos os usuários."""
        return self._request("GET", "/usuarios/")

    def create_user(self, user_data):
        """Cria um novo usuário."""
        return self._request("POST", "/usuarios/", data=user_data)
        
    def update_user_checkin(self, user_id, checkin_data):
        """Atualiza o humor e energia do usuário (check-in)."""
        return self._request("PUT", f"/usuarios/{user_id}", data=checkin_data)
    
    def update_user(self, user_id, user_data):
        """Atualiza um usuário existente."""
        return self._request("PUT", f"/usuarios/{user_id}", data=user_data)

    def delete_user(self, user_id):
        """Deleta um usuário."""
        return self._request("DELETE", f"/usuarios/{user_id}")

    # --- Métodos de Tarefa ---
    def get_all_tasks(self):
        """Busca todas as tarefas."""
        return self._request("GET", "/tarefas/") or []

    def create_task(self, task_data):
        """Cria uma nova tarefa."""
        return self._request("POST", "/tarefas/", data=task_data)

    def update_task(self, task_id, task_data):
        """Atualiza uma tarefa (inclusive para completar)."""
        return self._request("PUT", f"/tarefas/{task_id}", data=task_data)

    def delete_task(self, task_id):
        """Deleta uma tarefa."""
        return self._request("DELETE", f"/tarefas/{task_id}")

    # --- Métodos de Histórico ---
    def get_all_historicos(self):
        """Busca todos os registros de histórico."""
        return self._request("GET", "/historicos/") or []
        
    # --- Métodos de Agenda ---
    def get_all_agendas(self):
        """Busca todos os agendamentos."""
        return self._request("GET", "/agendas/") or []
    
    def create_agenda(self, agenda_data):
        """Agenda uma tarefa para uma data e hora."""
        return self._request("POST", "/agendas/", data=agenda_data)

    # --- Métodos de Dia Inativo ---
    def get_dias_inativos(self):
        """Busca todos os dias inativos."""
        return self._request("GET", "/dias-inativos/") or []
        
    def create_dia_inativo(self, dia_data):
        """Cria um dia inativo."""
        return self._request("POST", "/dias-inativos/", data=dia_data)

    def delete_dia_inativo(self, dia_id):
        """Deleta um dia inativo."""
        return self._request("DELETE", f"/dias-inativos/{dia_id}")
    
    
