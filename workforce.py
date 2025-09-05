"""
Exemplos de Uso do Sistema Workforce CAMEL-AI
=============================================

Este arquivo contém exemplos práticos de como usar o sistema Workforce
implementado, demonstrando diferentes cenários e casos de uso.
"""

from workforce_strategies import (
    WorkforceManager, Agent, Task, TaskExecutor,
    AgentRole, TaskStatus, CapabilityBasedStrategy,
    RoundRobinStrategy, PriorityBasedStrategy
)
import time
import json

def exemplo_basico():
    """Exemplo básico de uso do sistema workforce"""
    print("=== Exemplo Básico do Sistema Workforce ===\n")
    
    # Criar gerenciador com estratégia baseada em capacidades
    workforce = WorkforceManager(CapabilityBasedStrategy())
    
    # Registrar agentes com diferentes capacidades
    agentes = [
        Agent("agent_001", "Alice", AgentRole.WORKER, ["python", "data_analysis"], max_concurrent_tasks=2),
        Agent("agent_002", "Bob", AgentRole.WORKER, ["javascript", "web_development"], max_concurrent_tasks=1),
        Agent("agent_003", "Carol", AgentRole.SPECIALIST, ["python", "machine_learning", "data_analysis"], max_concurrent_tasks=3)
    ]
    
    for agent in agentes:
        workforce.register_agent(agent)
        print(f"Agente registrado: {agent.name} ({agent.role.value})")
    
    # Criar tarefas
    tarefas = [
        Task("task_001", "Análise de dados de vendas", ["python", "data_analysis"], priority=1),
        Task("task_002", "Desenvolvimento de dashboard web", ["javascript", "web_development"], priority=2),
        Task("task_003", "Treinamento de modelo ML", ["python", "machine_learning"], priority=3)
    ]
    
    # Submeter tarefas
    print("\n--- Submetendo Tarefas ---")
    for task in tarefas:
        success = workforce.submit_task(task)
        print(f"Tarefa {task.id}: {'Submetida' if success else 'Falhou'}")
    
    # Mostrar status
    print("\n--- Status do Workforce ---")
    status = workforce.get_workforce_status()
    print(json.dumps(status, indent=2))
    
    # Mostrar carga de trabalho dos agentes
    print("\n--- Carga de Trabalho dos Agentes ---")
    workload = workforce.get_agent_workload()
    for agent_id, info in workload.items():
        print(f"{info['name']}: {info['current_tasks']}/{info['max_concurrent']} tarefas "
              f"({info['utilization']:.1%} utilização)")

def exemplo_com_dependencias():
    """Exemplo demonstrando tarefas com dependências"""
    print("\n\n=== Exemplo com Dependências de Tarefas ===\n")
    
    workforce = WorkforceManager(PriorityBasedStrategy())
    
    # Registrar agentes
    agentes = [
        Agent("dev_001", "Developer 1", AgentRole.WORKER, ["coding", "testing"], max_concurrent_tasks=2),
        Agent("dev_002", "Developer 2", AgentRole.WORKER, ["coding", "deployment"], max_concurrent_tasks=2),
        Agent("qa_001", "QA Specialist", AgentRole.SPECIALIST, ["testing", "validation"], max_concurrent_tasks=1)
    ]
    
    for agent in agentes:
        workforce.register_agent(agent)
    
    executor = TaskExecutor(workforce)
    
    print("--- Pipeline de Desenvolvimento (Execução Sequencial) ---")
    
    # 1. Submeter e executar design
    design_task = Task("design", "Design da aplicação", ["coding"], priority=1)
    success = workforce.submit_task(design_task)
    print(f"Tarefa design: {'[OK] Submetida' if success else '[ERRO] Falhou'}")
    
    if design_task.status == TaskStatus.IN_PROGRESS:
        print("Executando design...")
        executor.simulate_task_execution("design", success_probability=0.9)
        time.sleep(0.2)
    
    # 2. Submeter e executar implementação (após design concluído)
    implement_task = Task("implement", "Implementação", ["coding"], priority=2, dependencies=["design"])
    success = workforce.submit_task(implement_task)
    print(f"Tarefa implement: {'[OK] Submetida' if success else '[ERRO] Falhou (dependencias nao atendidas)'}")
    
    if implement_task.status == TaskStatus.IN_PROGRESS:
        print("Executando implement...")
        executor.simulate_task_execution("implement", success_probability=0.9)
        time.sleep(0.2)
    
    # 3. Submeter e executar testes (após implementação concluída)
    test_task = Task("test", "Testes unitários", ["testing"], priority=3, dependencies=["implement"])
    success = workforce.submit_task(test_task)
    print(f"Tarefa test: {'[OK] Submetida' if success else '[ERRO] Falhou (dependencias nao atendidas)'}")
    
    if test_task.status == TaskStatus.IN_PROGRESS:
        print("Executando test...")
        executor.simulate_task_execution("test", success_probability=0.9)
        time.sleep(0.2)
    
    # 4. Submeter e executar deploy (após testes concluídos)
    deploy_task = Task("deploy", "Deploy da aplicação", ["deployment"], priority=4, dependencies=["test"])
    success = workforce.submit_task(deploy_task)
    print(f"Tarefa deploy: {'[OK] Submetida' if success else '[ERRO] Falhou (dependencias nao atendidas)'}")
    
    if deploy_task.status == TaskStatus.IN_PROGRESS:
        print("Executando deploy...")
        executor.simulate_task_execution("deploy", success_probability=0.9)
        time.sleep(0.2)
    
    # Status final
    print("\n--- Status Final ---")
    status = workforce.get_workforce_status()
    print(f"Tarefas concluídas: {status['completed_tasks']}")
    print(f"Tarefas falhadas: {status['failed_tasks']}")
    print(f"Pipeline completo: {'[OK] Sucesso' if status['completed_tasks'] == 4 else '[ERRO] Incompleto'}")

def exemplo_com_eventos():
    """Exemplo demonstrando sistema de eventos"""
    print("\n\n=== Exemplo com Sistema de Eventos ===\n")
    
    workforce = WorkforceManager(RoundRobinStrategy())
    
    # Definir handlers de eventos
    def on_task_assigned(event_type, data):
        print(f"[TASK] Tarefa {data['task_id']} atribuida ao agente {data['agent_id']}")
    
    def on_task_completed(event_type, data):
        print(f"[OK] Tarefa {data['task_id']} concluida com sucesso!")
    
    def on_task_failed(event_type, data):
        print(f"[ERRO] Tarefa {data['task_id']} falhou: {data.get('reason', 'Motivo desconhecido')}")
    
    def on_agent_registered(event_type, data):
        print(f"[AGENT] Novo agente registrado: {data['agent_id']}")
    
    # Registrar handlers
    workforce.add_event_handler('task_assigned', on_task_assigned)
    workforce.add_event_handler('task_completed', on_task_completed)
    workforce.add_event_handler('task_failed', on_task_failed)
    workforce.add_event_handler('agent_registered', on_agent_registered)
    
    # Registrar agentes
    agentes = [
        Agent("worker_1", "Worker Alpha", AgentRole.WORKER, ["general"], max_concurrent_tasks=1),
        Agent("worker_2", "Worker Beta", AgentRole.WORKER, ["general"], max_concurrent_tasks=1)
    ]
    
    for agent in agentes:
        workforce.register_agent(agent)
    
    # Criar e submeter tarefas
    tarefas = [
        Task("job_1", "Tarefa simples 1", ["general"]),
        Task("job_2", "Tarefa simples 2", ["general"]),
        Task("job_3", "Tarefa simples 3", ["general"])
    ]
    
    print("\n--- Submetendo Tarefas ---")
    for task in tarefas:
        workforce.submit_task(task)
    
    # Simular execução com algumas falhas
    executor = TaskExecutor(workforce)
    print("\n--- Simulando Execução ---")
    
    for task_id in ["job_1", "job_2", "job_3"]:
        if task_id in workforce.tasks:
            task = workforce.tasks[task_id]
            if task.status == TaskStatus.IN_PROGRESS:
                # Simular falha na segunda tarefa
                success_prob = 0.2 if task_id == "job_2" else 0.9
                executor.simulate_task_execution(task_id, success_probability=success_prob)
                time.sleep(0.3)

def exemplo_metricas_performance():
    """Exemplo demonstrando métricas de performance dos agentes"""
    print("\n\n=== Exemplo de Métricas de Performance ===\n")
    
    workforce = WorkforceManager(CapabilityBasedStrategy())
    
    # Registrar agentes
    agentes = [
        Agent("expert", "Expert Agent", AgentRole.SPECIALIST, ["complex_task"], max_concurrent_tasks=1),
        Agent("novice", "Novice Agent", AgentRole.WORKER, ["complex_task"], max_concurrent_tasks=1)
    ]
    
    for agent in agentes:
        workforce.register_agent(agent)
    
    # Executar múltiplas tarefas para gerar métricas
    executor = TaskExecutor(workforce)
    
    print("--- Executando Tarefas para Gerar Métricas ---")
    for i in range(10):
        task = Task(f"perf_task_{i}", f"Tarefa de performance {i}", ["complex_task"])
        workforce.submit_task(task)
        
        # Simular execução com diferentes taxas de sucesso por agente
        if task.status == TaskStatus.IN_PROGRESS:
            agent_id = task.assigned_agent
            # Expert tem maior taxa de sucesso
            success_prob = 0.9 if agent_id == "expert" else 0.6
            executor.simulate_task_execution(task.id, success_probability=success_prob)
    
    # Mostrar métricas finais
    print("\n--- Métricas de Performance ---")
    workload = workforce.get_agent_workload()
    
    for agent_id, info in workload.items():
        metrics = info['performance_metrics']
        print(f"\n{info['name']} ({info['role']}):")
        print(f"  Total de tarefas: {metrics.get('total_tasks', 0)}")
        print(f"  Tarefas bem-sucedidas: {metrics.get('successful_tasks', 0)}")
        print(f"  Taxa de sucesso: {metrics.get('success_rate', 0):.1%}")

def exemplo_dependencias_automaticas():
    """Exemplo demonstrando processamento automático de dependências"""
    print("\n\n=== Exemplo de Dependências Automáticas ===\n")
    
    workforce = WorkforceManager(CapabilityBasedStrategy())
    
    # Registrar agentes
    agentes = [
        Agent("worker_1", "Worker 1", AgentRole.WORKER, ["task_a", "task_b", "task_c"], max_concurrent_tasks=1),
        Agent("worker_2", "Worker 2", AgentRole.WORKER, ["task_a", "task_b", "task_c"], max_concurrent_tasks=1)
    ]
    
    for agent in agentes:
        workforce.register_agent(agent)
    
    # Criar todas as tarefas (algumas falharão por dependências)
    tarefas = [
        Task("step_1", "Primeira etapa", ["task_a"]),
        Task("step_2", "Segunda etapa", ["task_b"], dependencies=["step_1"]),
        Task("step_3", "Terceira etapa", ["task_c"], dependencies=["step_2"]),
        Task("parallel_1", "Tarefa paralela 1", ["task_a"]),  # Sem dependências
        Task("parallel_2", "Tarefa paralela 2", ["task_b"])   # Sem dependências
    ]
    
    print("--- Submetendo Todas as Tarefas ---")
    for task in tarefas:
        success = workforce.submit_task(task)
        status = "[OK] Submetida" if success else "[PENDENTE] Aguardando dependências"
        print(f"Tarefa {task.id}: {status}")
    
    print("\n--- Status Inicial ---")
    status = workforce.get_workforce_status()
    print(f"Em progresso: {status['in_progress_tasks']}, Pendentes: {status['pending_tasks']}")
    
    # Executar tarefas que estão em progresso
    executor = TaskExecutor(workforce)
    
    print("\n--- Execução Automática ---")
    # Simular execução até todas as tarefas serem processadas
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        # Encontrar tarefas em progresso
        tasks_in_progress = [
            task_id for task_id, task in workforce.tasks.items()
            if task.status == TaskStatus.IN_PROGRESS
        ]
        
        if not tasks_in_progress:
            break
            
        # Executar uma tarefa em progresso
        task_id = tasks_in_progress[0]
        print(f"Executando {task_id}...")
        executor.simulate_task_execution(task_id, success_probability=0.9)
        
        # Mostrar status após execução
        status = workforce.get_workforce_status()
        print(f"  Status: {status['in_progress_tasks']} em progresso, {status['pending_tasks']} pendentes, {status['completed_tasks']} concluídas")
        
        iteration += 1
        time.sleep(0.1)
    
    print("\n--- Resultado Final ---")
    final_status = workforce.get_workforce_status()
    print(f"Tarefas concluídas: {final_status['completed_tasks']}/{len(tarefas)}")
    print(f"Tarefas falhadas: {final_status['failed_tasks']}")
    
    # Mostrar ordem de execução
    print("\n--- Ordem de Execução ---")
    for task_id, task in workforce.tasks.items():
        status_str = "[OK]" if task.status == TaskStatus.COMPLETED else "[ERRO]" if task.status == TaskStatus.FAILED else "[PENDENTE]"
        deps_str = f" (deps: {task.dependencies})" if task.dependencies else ""
        print(f"  {task_id}: {status_str}{deps_str}")

def exemplo_estrategias_diferentes():
    """Exemplo comparando diferentes estratégias de atribuição"""
    print("\n\n=== Comparação de Estratégias de Atribuição ===\n")
    
    estrategias = [
        ("Round Robin", RoundRobinStrategy()),
        ("Baseada em Capacidades", CapabilityBasedStrategy()),
        ("Baseada em Prioridade", PriorityBasedStrategy())
    ]
    
    for nome_estrategia, estrategia in estrategias:
        print(f"--- Testando Estratégia: {nome_estrategia} ---")
        
        workforce = WorkforceManager(estrategia)
        
        # Registrar agentes com diferentes capacidades
        agentes = [
            Agent("specialist", "Specialist", AgentRole.SPECIALIST, 
                  ["python", "ml", "data"], max_concurrent_tasks=2),
            Agent("generalist", "Generalist", AgentRole.WORKER, 
                  ["python", "web"], max_concurrent_tasks=3),
            Agent("junior", "Junior", AgentRole.WORKER, 
                  ["python"], max_concurrent_tasks=1)
        ]
        
        for agent in agentes:
            workforce.register_agent(agent)
        
        # Criar tarefas variadas
        tarefas = [
            Task("ml_task", "Tarefa de ML", ["python", "ml"]),
            Task("web_task", "Tarefa Web", ["python", "web"]),
            Task("data_task", "Tarefa de Dados", ["python", "data"]),
            Task("simple_task", "Tarefa Simples", ["python"])
        ]
        
        # Submeter tarefas e ver atribuições
        for task in tarefas:
            workforce.submit_task(task)
            if task.assigned_agent:
                agent_name = workforce.agents[task.assigned_agent].name
                print(f"  {task.id} -> {agent_name}")
        
        print()

if __name__ == "__main__":
    # Executar todos os exemplos
    exemplo_basico()
    exemplo_com_dependencias()
    exemplo_com_eventos()
    exemplo_metricas_performance()
    exemplo_estrategias_diferentes()
    
    print("\n" + "="*50)
    print("Todos os exemplos executados com sucesso!")
    print("="*50)