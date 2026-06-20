from __future__ import annotations

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, before_kickoff, crew, task

from veloserve_ai_amp.context import build_shared_context


@CrewBase
class VeloserveAiAmpCrew:
    """AMP-ready VeloServe orchestrator crew."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @before_kickoff
    def prepare_inputs(self, inputs: dict | None):
        payload = dict(inputs or {})
        payload.setdefault("goal", "Review the current VeloServe task and propose the best next steps.")
        payload.setdefault("repo_scope", "all relevant repos")
        payload.setdefault(
            "constraints",
            "Do not deploy, do not change billing or pricing without approval, and keep work small and reviewable.",
        )
        payload.setdefault(
            "success_definition",
            "Return a markdown result with recommended owner crew, repo scope, implementation plan, and risk notes.",
        )
        payload["shared_context"] = build_shared_context()
        return payload

    @agent
    def intake_router(self) -> Agent:
        cfg = dict(self.agents_config["intake_router"])  # type: ignore[index]
        cfg["backstory"] = cfg["backstory"] + "\n\n{shared_context}"
        return Agent(config=cfg, verbose=True)

    @agent
    def implementation_planner(self) -> Agent:
        cfg = dict(self.agents_config["implementation_planner"])  # type: ignore[index]
        cfg["backstory"] = cfg["backstory"] + "\n\n{shared_context}"
        return Agent(config=cfg, verbose=True)

    @agent
    def qa_gatekeeper(self) -> Agent:
        cfg = dict(self.agents_config["qa_gatekeeper"])  # type: ignore[index]
        cfg["backstory"] = cfg["backstory"] + "\n\n{shared_context}"
        return Agent(config=cfg, verbose=True)

    @task
    def route_task(self) -> Task:
        return Task(config=self.tasks_config["route_task"])  # type: ignore[index]

    @task
    def plan_task(self) -> Task:
        return Task(config=self.tasks_config["plan_task"])  # type: ignore[index]

    @task
    def review_task(self) -> Task:
        return Task(config=self.tasks_config["review_task"])  # type: ignore[index]

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
