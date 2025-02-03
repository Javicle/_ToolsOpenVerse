import abc
import asyncio
from abc import abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from tools_openverse.common.logger_ import setup_logger

console = Console()


class ServiceStatusResponse(BaseModel):
    service_name: str
    success: bool
    message: str

    last_check: Optional[datetime] = None
    response_time_ms: Optional[float] = None


class ServiceCheck(abc.ABC):
    def __init__(self, service_name: str, **kwargs: Any):
        self.service_name = service_name
        self.kwargs = kwargs

    @abstractmethod
    async def check(self) -> ServiceStatusResponse:
        raise NotImplementedError


class HealthCheck:
    def __init__(self) -> None:
        self._services: dict[str, ServiceCheck] = {}
        self._logger = setup_logger("health_check")

    async def add_service(self, service: ServiceCheck) -> None:
        """Добавляет сервис для проверки здоровья."""
        if service.service_name in self._services:
            self._logger.warning(f"Service {service.service_name} already exists")
            return

        self._services[service.service_name] = service
        self._logger.info(f"Service {service.service_name} added")

    async def remove_service(self, service_name: str) -> None:
        """Удаляет сервис из проверки здоровья."""
        if service_name in self._services:
            del self._services[service_name]
            self._logger.info(f"Service {service_name} removed")
        else:
            self._logger.warning(f"Service {service_name} not found")

    async def check_services(self) -> dict[str, ServiceStatusResponse]:
        results: dict[str, ServiceStatusResponse] = {}

        async def _check_service(service: ServiceCheck) -> None:

            start_time = datetime.now()
            try:
                status = await service.check()
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000

                status.last_check = end_time
                status.response_time_ms = response_time
                results[service.service_name] = status
            except Exception as e:
                self._logger.error(
                    f"Error checking service {service.service_name}: {str(e)}"
                )
                results[service.service_name] = ServiceStatusResponse(
                    service_name=service.service_name,
                    success=False,
                    message=f"Check failed: {str(e)}",
                    last_check=datetime.now(),
                )

        await asyncio.gather(
            *[_check_service(service) for service in self._services.values()]
        )
        return results

    async def display_start_message(self) -> None:
        """Красивая таблица с информацией о сервисах."""
        table = Table(title="Service Heath Status")

        table.add_column("Service", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Details", style="green")

        results_status = await self.check_services()
        for service in results_status.values():
            table.add_row(
                service.service_name,
                "✅ Connected" if service.success is True else "❌ Failed",
                f"Last check: {
                    service.last_check} | Response time: {
                        service.response_time_ms} ms | Message: {service.message}",
                service.message,
            )

            console.print("\n")
            console.print(
                Panel.fit("🚀 FastAPI Service Status Check", style="bold white")
            )
            console.print(table)
            console.print("\n")
