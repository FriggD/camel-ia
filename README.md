# Sistema Workforce CAMEL-AI - Implementação Funcional

Este projeto implementa uma versão funcional do sistema **Workforce** do CAMEL-AI, baseado na documentação oficial. O sistema permite gerenciar agentes de IA, distribuir tarefas entre eles e coordenar execução com dependências.

## 📋 O que é o Projeto

O **Workforce** é um módulo do CAMEL-AI que simula um ambiente de trabalho colaborativo onde múltiplos agentes de IA podem:
- Receber e executar tarefas específicas
- Trabalhar com diferentes capacidades e especializações
- Coordenar execução de tarefas com dependências
- Monitorar performance e métricas
- Emitir eventos para observabilidade

## 🏗️ Arquitetura do Sistema

### Componentes Principais

1. **WorkforceManager**: Gerenciador central que coordena agentes e tarefas
2. **Agent**: Representa um agente de IA com capacidades específicas
3. **Task**: Representa uma tarefa com requisitos e dependências
4. **WorkforceStrategy**: Estratégias para atribuição de tarefas aos agentes
5. **TaskExecutor**: Simulador de execução de tarefas

### Estratégias de Atribuição

- **CapabilityBasedStrategy**: Atribui tarefas baseado nas capacidades dos agentes
- **RoundRobinStrategy**: Distribui tarefas em rotação entre agentes
- **PriorityBasedStrategy**: Considera prioridade e carga de trabalho

## 🚀 Como Executar o Projeto

### Pré-requisitos

```bash
# Python 3.8 ou superior
python --version
```

### Instalação

```bash
# Clone o repositório
git clone https://github.com/FriggD/camel-ia.git
cd camel-ia

# Não há dependências externas - usa apenas bibliotecas padrão do Python
```

### Execução dos Exemplos

#### 1. Executar Exemplos Completos

```bash
python workforce.py
```

**O que acontece:**
- Executa 5 exemplos diferentes demonstrando funcionalidades
- Mostra saída detalhada de cada operação
- Demonstra diferentes estratégias e cenários

#### 2. Executar Testes Unitários

```bash
python -m unittest workforce-unitTest.py -v
```

**O que acontece:**
- Executa 15+ testes unitários
- Valida funcionamento de cada componente
- Testa cenários de erro e edge cases

#### 3. Uso Programático

```python
from workforce_strategies import WorkforceManager, Agent, Task, AgentRole

# Criar gerenciador
workforce = WorkforceManager()

# Registrar agente
agent = Agent("dev_001", "Developer", AgentRole.WORKER, ["python"])
workforce.register_agent(agent)

# Submeter tarefa
task = Task("task_001", "Desenvolver feature", ["python"])
workforce.submit_task(task)

# Verificar status
status = workforce.get_workforce_status()
print(f"Tarefas em progresso: {status['in_progress_tasks']}")
```

## 📁 Estrutura dos Arquivos

### `workforce_strategies.py`
**Implementação principal do sistema**

- **Classes de Dados**: `Task`, `Agent`, `TaskStatus`, `AgentRole`
- **Estratégias**: `WorkforceStrategy` e implementações concretas
- **Gerenciador**: `WorkforceManager` - coordena todo o sistema
- **Executor**: `TaskExecutor` - simula execução de tarefas

### `workforce.py`
**Exemplos práticos de uso**

- **exemplo_basico()**: Demonstra uso básico com 3 agentes e 3 tarefas
- **exemplo_com_dependencias()**: Pipeline sequencial (design → implement → test → deploy)
- **exemplo_com_eventos()**: Sistema de eventos e handlers
- **exemplo_metricas_performance()**: Coleta de métricas de agentes
- **exemplo_estrategias_diferentes()**: Comparação entre estratégias

### `workforce-unitTest.py`
**Testes unitários completos**

- **TestWorkforceManager**: Testa gerenciamento de agentes e tarefas
- **TestAgent/TestTask**: Testa criação e propriedades
- **TestStrategies**: Valida lógica de atribuição
- **TestTaskDependencies**: Testa cadeia de dependências
- **TestEventSystem**: Valida sistema de eventos

## 🔍 Explicação Detalhada da Execução

### Quando você executa `python workforce.py`:

#### 1. **Exemplo Básico**
```
=== Exemplo Básico do Sistema Workforce ===

Agente registrado: Alice (worker)
Agente registrado: Bob (worker) 
Agente registrado: Carol (specialist)

--- Submetendo Tarefas ---
Tarefa task_001: Submetida
Tarefa task_002: Submetida
Tarefa task_003: Submetida
```

**O que acontece:**
- Cria 3 agentes com capacidades diferentes
- Submete 3 tarefas com requisitos específicos
- Sistema automaticamente atribui tarefas aos agentes adequados
- Mostra status e utilização dos agentes

#### 2. **Exemplo com Dependências**
```
--- Pipeline de Desenvolvimento (Execução Sequencial) ---
Tarefa design: [OK] Submetida
Executando design...
Tarefa implement: [OK] Submetida
Executando implement...
```

**O que acontece:**
- Cria pipeline: design → implement → test → deploy
- Tarefas só são executadas após dependências serem concluídas
- Simula execução real com delays e probabilidade de falha
- Mostra status final do pipeline

#### 3. **Sistema de Eventos**
```
[AGENT] Novo agente registrado: worker_1
[TASK] Tarefa job_1 atribuida ao agente worker_1
[OK] Tarefa job_1 concluida com sucesso!
[ERRO] Tarefa job_2 falhou: Simulated failure
```

**O que acontece:**
- Registra handlers para eventos do sistema
- Mostra em tempo real: registros, atribuições, conclusões, falhas
- Demonstra observabilidade do sistema

### Quando você executa os testes:

```bash
python -m unittest workforce-unitTest.py -v
```

**Saída esperada:**
```
test_agent_creation ... ok
test_complete_task ... ok
test_dependency_chain ... ok
test_register_agent ... ok
...
----------------------------------------------------------------------
Ran 15 tests in 0.123s

OK
```

**O que é testado:**
- ✅ Registro e remoção de agentes
- ✅ Submissão e conclusão de tarefas
- ✅ Validação de dependências
- ✅ Estratégias de atribuição
- ✅ Sistema de eventos
- ✅ Métricas de performance
- ✅ Cenários de erro

## 🎯 Casos de Uso Demonstrados

1. **Desenvolvimento de Software**: Pipeline automatizado (design → code → test → deploy)
2. **Análise de Dados**: Distribuição de tarefas entre especialistas
3. **Processamento Paralelo**: Múltiplas tarefas independentes
4. **Workflow Complexo**: Tarefas com múltiplas dependências
5. **Monitoramento**: Métricas de performance e observabilidade

## 🔧 Funcionalidades Implementadas

- ✅ **Gerenciamento de Agentes**: Registro, remoção, capacidades
- ✅ **Sistema de Tarefas**: Criação, atribuição, execução, dependências
- ✅ **Estratégias de Atribuição**: 3 estratégias diferentes implementadas
- ✅ **Sistema de Eventos**: Observabilidade completa
- ✅ **Métricas**: Performance e utilização dos agentes
- ✅ **Simulação**: Executor para demonstração prática
- ✅ **Testes**: Cobertura completa com testes unitários

## 📊 Métricas e Observabilidade

O sistema coleta automaticamente:
- **Taxa de sucesso** por agente
- **Utilização** (tarefas atuais/máximo)
- **Total de tarefas** executadas
- **Status em tempo real** do workforce
- **Eventos** de todas as operações

## 🎓 Valor Educacional

Este projeto demonstra:
- **Padrões de Design**: Strategy, Observer, Factory
- **Arquitetura de Sistemas**: Separação de responsabilidades
- **Testes Unitários**: Cobertura completa e casos edge
- **Documentação**: Código bem documentado e exemplos práticos
- **Simulação**: Como testar sistemas complexos

---

**Baseado na documentação oficial**: https://docs.camel-ai.org/key_modules/workforce
**Com intuito educativo, feito por:** [Matheus Bueno Bartkevicius](https://github.com/xBu3n0) e [Glaucia Dias](https://github.com/FriggD)
