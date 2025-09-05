"""
CAMEL-AI Workforce Modeling - Implementação Funcional
====================================================

Este módulo implementa uma modelagem funcional do sistema Workforce do CAMEL-AI,
baseado na documentação oficial: https://docs.camel-ai.org/key_modules/workforce

"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from abc import ABC, abstractmethod

class TaskStatus(Enum):
    """Status possíveis para uma tarefa no workforce"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentRole(Enum):
    """Papéis disponíveis para agentes no workforce"""
    WORKER = "worker"
    SUPERVISOR = "supervisor"
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"

@dataclass
class Task:
    """Representa uma tarefa individual no sistema workforce"""
    id: str
    description: str
    requirements: List[str]
    priority: int = 1
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    result: Optional[Any] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Agent:
    """Representa um agente no workforce"""
    id: str
    name: str
    role: AgentRole
    capabilities: List[str]
    max_concurrent_tasks: int = 1
    current_tasks: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    is_active: bool = True

class WorkforceStrategy(ABC):
    """Interface abstrata para estratégias de distribuição de tarefas"""
    
    @abstractmethod
    def assign_task(self, task: Task, available_agents: List[Agent]) -> Optional[Agent]:
        """Atribui uma tarefa a um agente disponível"""
        pass

class RoundRobinStrategy(WorkforceStrategy):
    """Estratégia Round Robin para distribuição de tarefas"""
    
    def __init__(self):
        self.last_assigned_index = -1
    
    def assign_task(self, task: Task, available_agents: List[Agent]) -> Optional[Agent]:
        if not available_agents:
            return None
        
        self.last_assigned_index = (self.last_assigned_index + 1) % len(available_agents)
        return available_agents[self.last_assigned_index]

class CapabilityBasedStrategy(WorkforceStrategy):
    """Estratégia baseada em capacidades para distribuição de tarefas"""
    
    def assign_task(self, task: Task, available_agents: List[Agent]) -> Optional[Agent]:
        suitable_agents = []
        
        for agent in available_agents:
            # Verifica se o agente tem as capacidades necessárias
            if all(req in agent.capabilities for req in task.requirements):
                suitable_agents.append(agent)
        
        if not suitable_agents:
            return None
        
        # Seleciona o agente com melhor performance
        return max(suitable_agents, 
                  key=lambda a: a.performance_metrics.get('success_rate', 0.0))

class PriorityBasedStrategy(WorkforceStrategy):
    """Estratégia baseada em prioridade e carga de trabalho"""
    
    def assign_task(self, task: Task, available_agents: List[Agent]) -> Optional[Agent]:
        suitable_agents = [
            agent for agent in available_agents
            if all(req in agent.capabilities for req in task.requirements)
            and len(agent.current_tasks) < agent.max_concurrent_tasks
        ]
        
        if not suitable_agents:
            return None
        
        # Prioriza agentes com menor carga de trabalho
        return min(suitable_agents, key=lambda a: len(a.current_tasks))

class WorkforceManager:
    """Gerenciador principal do sistema workforce"""
    
    def __init__(self, strategy: WorkforceStrategy = None):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []
        self.strategy = strategy or CapabilityBasedStrategy()
        self.event_handlers: Dict[str, List[Callable]] = {}
    
    def register_agent(self, agent: Agent) -> None:
        """Registra um novo agente no workforce"""
        self.agents[agent.id] = agent
        self._emit_event('agent_registered', {'agent_id': agent.id})
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove um agente do workforce"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            # Reassign tasks if agent has active tasks
            for task_id in agent.current_tasks:
                self._reassign_task(task_id)
            
            del self.agents[agent_id]
            self._emit_event('agent_removed', {'agent_id': agent_id})
            return True
        return False
    
    def submit_task(self, task: Task) -> bool:
        """Submete uma nova tarefa para o workforce"""
        # Verifica dependências
        for dep_id in task.dependencies:
            if dep_id not in self.tasks or self.tasks[dep_id].status != TaskStatus.COMPLETED:
                return False
        
        self.tasks[task.id] = task
        self.task_queue.append(task.id)
        self._emit_event('task_submitted', {'task_id': task.id})
        
        # Tenta atribuir imediatamente
        self._process_task_queue()
        return True
    
    def _process_task_queue(self) -> None:
        """Processa a fila de tarefas pendentes"""
        processed_tasks = []
        
        for task_id in self.task_queue:
            task = self.tasks[task_id]
            if task.status != TaskStatus.PENDING:
                processed_tasks.append(task_id)
                continue
            
            available_agents = self._get_available_agents()
            assigned_agent = self.strategy.assign_task(task, available_agents)
            
            if assigned_agent:
                self._assign_task_to_agent(task, assigned_agent)
                processed_tasks.append(task_id)
        
        # Remove tarefas processadas da fila
        for task_id in processed_tasks:
            self.task_queue.remove(task_id)
    
    def _get_available_agents(self) -> List[Agent]:
        """Retorna lista de agentes disponíveis"""
        return [
            agent for agent in self.agents.values()
            if agent.is_active and len(agent.current_tasks) < agent.max_concurrent_tasks
        ]
    
    def _assign_task_to_agent(self, task: Task, agent: Agent) -> None:
        """Atribui uma tarefa específica a um agente"""
        task.assigned_agent = agent.id
        task.status = TaskStatus.IN_PROGRESS
        agent.current_tasks.append(task.id)
        
        self._emit_event('task_assigned', {
            'task_id': task.id,
            'agent_id': agent.id
        })
    
    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """Marca uma tarefa como concluída"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status != TaskStatus.IN_PROGRESS:
            return False
        
        task.status = TaskStatus.COMPLETED
        task.result = result
        
        # Remove da lista de tarefas do agente
        if task.assigned_agent:
            agent = self.agents[task.assigned_agent]
            agent.current_tasks.remove(task_id)
            
            # Atualiza métricas de performance
            self._update_agent_metrics(agent, success=True)
        
        self._emit_event('task_completed', {'task_id': task_id})
        
        # Processa tarefas dependentes
        self._process_dependent_tasks(task_id)
        
        # Processa fila novamente
        self._process_task_queue()
        return True
    
    def fail_task(self, task_id: str, reason: str = None) -> bool:
        """Marca uma tarefa como falhada"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status != TaskStatus.IN_PROGRESS:
            return False
        
        task.status = TaskStatus.FAILED
        task.metadata['failure_reason'] = reason
        
        # Remove da lista de tarefas do agente
        if task.assigned_agent:
            agent = self.agents[task.assigned_agent]
            agent.current_tasks.remove(task_id)
            
            # Atualiza métricas de performance
            self._update_agent_metrics(agent, success=False)
        
        self._emit_event('task_failed', {'task_id': task_id, 'reason': reason})
        return True
    
    def _reassign_task(self, task_id: str) -> None:
        """Reassigna uma tarefa para outro agente"""
        task = self.tasks[task_id]
        if task.assigned_agent:
            agent = self.agents[task.assigned_agent]
            agent.current_tasks.remove(task_id)
        
        task.assigned_agent = None
        task.status = TaskStatus.PENDING
        self.task_queue.append(task_id)
    
    def _process_dependent_tasks(self, completed_task_id: str) -> None:
        """Processa tarefas que dependem da tarefa concluída"""
        for task in self.tasks.values():
            if (completed_task_id in task.dependencies and 
                task.status == TaskStatus.PENDING and
                task.id not in self.task_queue):
                
                # Verifica se todas as dependências foram concluídas
                all_deps_completed = all(
                    self.tasks[dep_id].status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                    if dep_id in self.tasks
                )
                
                if all_deps_completed:
                    self.task_queue.append(task.id)
    
    def _update_agent_metrics(self, agent: Agent, success: bool) -> None:
        """Atualiza métricas de performance do agente"""
        if 'total_tasks' not in agent.performance_metrics:
            agent.performance_metrics['total_tasks'] = 0
            agent.performance_metrics['successful_tasks'] = 0
        
        agent.performance_metrics['total_tasks'] += 1
        if success:
            agent.performance_metrics['successful_tasks'] += 1
        
        # Calcula taxa de sucesso
        total = agent.performance_metrics['total_tasks']
        successful = agent.performance_metrics['successful_tasks']
        agent.performance_metrics['success_rate'] = successful / total if total > 0 else 0.0
    
    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """Adiciona um handler para eventos do workforce"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emite um evento para os handlers registrados"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_type, data)
                except Exception as e:
                    print(f"Error in event handler: {e}")
    
    def get_workforce_status(self) -> Dict[str, Any]:
        """Retorna status atual do workforce"""
        return {
            'total_agents': len(self.agents),
            'active_agents': len([a for a in self.agents.values() if a.is_active]),
            'total_tasks': len(self.tasks),
            'pending_tasks': len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            'in_progress_tasks': len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
            'completed_tasks': len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
            'failed_tasks': len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED]),
            'queue_length': len(self.task_queue)
        }
    
    def get_agent_workload(self) -> Dict[str, Dict[str, Any]]:
        """Retorna informações de carga de trabalho dos agentes"""
        workload = {}
        for agent_id, agent in self.agents.items():
            workload[agent_id] = {
                'name': agent.name,
                'role': agent.role.value,
                'current_tasks': len(agent.current_tasks),
                'max_concurrent': agent.max_concurrent_tasks,
                'utilization': len(agent.current_tasks) / agent.max_concurrent_tasks,
                'performance_metrics': agent.performance_metrics.copy()
            }
        return workload

# Classe auxiliar para simulação de execução de tarefas
class TaskExecutor:
    """Simulador de execução de tarefas para demonstração"""
    
    def __init__(self, workforce_manager: WorkforceManager):
        self.workforce_manager = workforce_manager
    
    def simulate_task_execution(self, task_id: str, success_probability: float = 0.8) -> bool:
        """Simula a execução de uma tarefa"""
        import random
        
        if task_id not in self.workforce_manager.tasks:
            return False
        
        task = self.workforce_manager.tasks[task_id]
        if task.status != TaskStatus.IN_PROGRESS:
            return False
        
        # Simula tempo de processamento
        import time
        time.sleep(0.1)  # Simula processamento
        
        # Determina sucesso baseado na probabilidade
        if random.random() < success_probability:
            result = f"Task {task_id} completed successfully"
            return self.workforce_manager.complete_task(task_id, result)
        else:
            return self.workforce_manager.fail_task(task_id, "Simulated failure")