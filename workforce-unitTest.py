"""
Testes Unitários para o Sistema Workforce CAMEL-AI
==================================================

Este arquivo contém testes unitários para validar o funcionamento
correto do sistema Workforce implementado.
"""

import unittest
from workforce_strategies import (
    WorkforceManager, Agent, Task, TaskExecutor,
    AgentRole, TaskStatus, CapabilityBasedStrategy,
    RoundRobinStrategy, PriorityBasedStrategy
)

class TestWorkforceManager(unittest.TestCase):
    """Testes para a classe WorkforceManager"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.workforce = WorkforceManager()
        self.agent = Agent("test_agent", "Test Agent", AgentRole.WORKER, ["python"])
        self.task = Task("test_task", "Test Task", ["python"])
    
    def test_register_agent(self):
        """Testa registro de agente"""
        self.workforce.register_agent(self.agent)
        self.assertIn("test_agent", self.workforce.agents)
        self.assertEqual(self.workforce.agents["test_agent"], self.agent)
    
    def test_remove_agent(self):
        """Testa remoção de agente"""
        self.workforce.register_agent(self.agent)
        result = self.workforce.remove_agent("test_agent")
        self.assertTrue(result)
        self.assertNotIn("test_agent", self.workforce.agents)
    
    def test_remove_nonexistent_agent(self):
        """Testa remoção de agente inexistente"""
        result = self.workforce.remove_agent("nonexistent")
        self.assertFalse(result)
    
    def test_submit_task(self):
        """Testa submissão de tarefa"""
        self.workforce.register_agent(self.agent)
        result = self.workforce.submit_task(self.task)
        self.assertTrue(result)
        self.assertIn("test_task", self.workforce.tasks)
    
    def test_submit_task_with_dependencies(self):
        """Testa submissão de tarefa com dependências não atendidas"""
        task_with_deps = Task("dep_task", "Dependent Task", ["python"], dependencies=["missing_task"])
        result = self.workforce.submit_task(task_with_deps)
        self.assertFalse(result)
    
    def test_complete_task(self):
        """Testa conclusão de tarefa"""
        self.workforce.register_agent(self.agent)
        self.workforce.submit_task(self.task)
        
        # Tarefa deve estar em progresso
        self.assertEqual(self.task.status, TaskStatus.IN_PROGRESS)
        
        # Completar tarefa
        result = self.workforce.complete_task("test_task", "Test result")
        self.assertTrue(result)
        self.assertEqual(self.task.status, TaskStatus.COMPLETED)
        self.assertEqual(self.task.result, "Test result")
    
    def test_fail_task(self):
        """Testa falha de tarefa"""
        self.workforce.register_agent(self.agent)
        self.workforce.submit_task(self.task)
        
        result = self.workforce.fail_task("test_task", "Test failure")
        self.assertTrue(result)
        self.assertEqual(self.task.status, TaskStatus.FAILED)
        self.assertEqual(self.task.metadata['failure_reason'], "Test failure")
    
    def test_workforce_status(self):
        """Testa obtenção de status do workforce"""
        self.workforce.register_agent(self.agent)
        self.workforce.submit_task(self.task)
        
        status = self.workforce.get_workforce_status()
        self.assertEqual(status['total_agents'], 1)
        self.assertEqual(status['active_agents'], 1)
        self.assertEqual(status['total_tasks'], 1)
        self.assertEqual(status['in_progress_tasks'], 1)

class TestAgent(unittest.TestCase):
    """Testes para a classe Agent"""
    
    def test_agent_creation(self):
        """Testa criação de agente"""
        agent = Agent("agent_1", "Agent One", AgentRole.WORKER, ["skill1", "skill2"])
        self.assertEqual(agent.id, "agent_1")
        self.assertEqual(agent.name, "Agent One")
        self.assertEqual(agent.role, AgentRole.WORKER)
        self.assertEqual(agent.capabilities, ["skill1", "skill2"])
        self.assertTrue(agent.is_active)
        self.assertEqual(agent.max_concurrent_tasks, 1)

class TestTask(unittest.TestCase):
    """Testes para a classe Task"""
    
    def test_task_creation(self):
        """Testa criação de tarefa"""
        task = Task("task_1", "Task One", ["req1", "req2"], priority=2)
        self.assertEqual(task.id, "task_1")
        self.assertEqual(task.description, "Task One")
        self.assertEqual(task.requirements, ["req1", "req2"])
        self.assertEqual(task.priority, 2)
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertIsNone(task.assigned_agent)

class TestStrategies(unittest.TestCase):
    """Testes para estratégias de atribuição"""
    
    def setUp(self):
        """Configuração inicial"""
        self.agents = [
            Agent("agent_1", "Agent 1", AgentRole.WORKER, ["python"]),
            Agent("agent_2", "Agent 2", AgentRole.WORKER, ["javascript"]),
            Agent("agent_3", "Agent 3", AgentRole.SPECIALIST, ["python", "ml"])
        ]
        self.task_python = Task("py_task", "Python Task", ["python"])
        self.task_ml = Task("ml_task", "ML Task", ["python", "ml"])
    
    def test_capability_based_strategy(self):
        """Testa estratégia baseada em capacidades"""
        strategy = CapabilityBasedStrategy()
        
        # Tarefa Python - deve escolher agente com Python
        assigned = strategy.assign_task(self.task_python, self.agents)
        self.assertIn(assigned.id, ["agent_1", "agent_3"])
        
        # Tarefa ML - deve escolher especialista
        assigned = strategy.assign_task(self.task_ml, self.agents)
        self.assertEqual(assigned.id, "agent_3")
    
    def test_round_robin_strategy(self):
        """Testa estratégia round robin"""
        strategy = RoundRobinStrategy()
        
        # Primeira atribuição
        assigned1 = strategy.assign_task(self.task_python, self.agents)
        self.assertEqual(assigned1, self.agents[0])
        
        # Segunda atribuição
        assigned2 = strategy.assign_task(self.task_python, self.agents)
        self.assertEqual(assigned2, self.agents[1])
    
    def test_priority_based_strategy(self):
        """Testa estratégia baseada em prioridade"""
        strategy = PriorityBasedStrategy()
        
        # Adicionar tarefas aos agentes para testar carga
        self.agents[0].current_tasks = ["existing_task"]
        
        # Deve escolher agente com menor carga
        assigned = strategy.assign_task(self.task_python, self.agents)
        self.assertEqual(assigned.id, "agent_3")  # Agente sem carga atual

class TestTaskDependencies(unittest.TestCase):
    """Testes para dependências de tarefas"""
    
    def setUp(self):
        """Configuração inicial"""
        self.workforce = WorkforceManager()
        self.agent = Agent("agent", "Agent", AgentRole.WORKER, ["general"])
        self.workforce.register_agent(self.agent)
    
    def test_dependency_chain(self):
        """Testa cadeia de dependências"""
        # Criar tarefas em cadeia
        task1 = Task("task1", "First Task", ["general"])
        task2 = Task("task2", "Second Task", ["general"], dependencies=["task1"])
        task3 = Task("task3", "Third Task", ["general"], dependencies=["task2"])
        
        # Submeter tarefas - task2 e task3 falharão devido a dependências
        self.assertTrue(self.workforce.submit_task(task1))
        self.assertFalse(self.workforce.submit_task(task2))  # Falha: task1 não concluída
        self.assertFalse(self.workforce.submit_task(task3))  # Falha: task2 não existe
        
        # Apenas task1 deve estar em progresso
        self.assertEqual(task1.status, TaskStatus.IN_PROGRESS)
        
        # Completar task1
        self.workforce.complete_task("task1")
        
        # Agora podemos submeter task2
        self.assertTrue(self.workforce.submit_task(task2))
        self.assertEqual(task2.status, TaskStatus.IN_PROGRESS)
        
        # Completar task2 e submeter task3
        self.workforce.complete_task("task2")
        self.assertTrue(self.workforce.submit_task(task3))
        self.assertEqual(task3.status, TaskStatus.IN_PROGRESS)

class TestEventSystem(unittest.TestCase):
    """Testes para sistema de eventos"""
    
    def setUp(self):
        """Configuração inicial"""
        self.workforce = WorkforceManager()
        self.events_received = []
        
        def event_handler(event_type, data):
            self.events_received.append((event_type, data))
        
        self.workforce.add_event_handler('task_assigned', event_handler)
        self.workforce.add_event_handler('task_completed', event_handler)
    
    def test_event_emission(self):
        """Testa emissão de eventos"""
        agent = Agent("agent", "Agent", AgentRole.WORKER, ["general"])
        task = Task("task", "Task", ["general"])
        
        self.workforce.register_agent(agent)
        self.workforce.submit_task(task)
        
        # Deve ter recebido evento de atribuição
        self.assertEqual(len(self.events_received), 1)
        self.assertEqual(self.events_received[0][0], 'task_assigned')
        
        # Completar tarefa
        self.workforce.complete_task("task")
        
        # Deve ter recebido evento de conclusão
        self.assertEqual(len(self.events_received), 2)
        self.assertEqual(self.events_received[1][0], 'task_completed')

class TestPerformanceMetrics(unittest.TestCase):
    """Testes para métricas de performance"""
    
    def setUp(self):
        """Configuração inicial"""
        self.workforce = WorkforceManager()
        self.agent = Agent("agent", "Agent", AgentRole.WORKER, ["general"])
        self.workforce.register_agent(self.agent)
    
    def test_metrics_update(self):
        """Testa atualização de métricas"""
        # Executar algumas tarefas
        for i in range(3):
            task = Task(f"task_{i}", f"Task {i}", ["general"])
            self.workforce.submit_task(task)
            self.workforce.complete_task(f"task_{i}")
        
        # Verificar métricas
        metrics = self.agent.performance_metrics
        self.assertEqual(metrics['total_tasks'], 3)
        self.assertEqual(metrics['successful_tasks'], 3)
        self.assertEqual(metrics['success_rate'], 1.0)
        
        # Falhar uma tarefa
        task_fail = Task("task_fail", "Failing Task", ["general"])
        self.workforce.submit_task(task_fail)
        self.workforce.fail_task("task_fail")
        
        # Verificar métricas atualizadas
        self.assertEqual(metrics['total_tasks'], 4)
        self.assertEqual(metrics['successful_tasks'], 3)
        self.assertEqual(metrics['success_rate'], 0.75)

if __name__ == '__main__':
    # Executar todos os testes
    unittest.main(verbosity=2)