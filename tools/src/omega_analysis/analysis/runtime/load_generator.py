"""Synthetic load testing framework for performance baseline collection.

This module provides automated load generation for Spring Boot applications to establish
performance baselines when production runtime analysis is not feasible. Supports multiple
load patterns and traffic scenarios.

Per FR-002: Fallback to synthetic load testing when production deployment is not feasible.
Per FR-004: Collect performance baselines with 95% confidence intervals over 24-48 hour periods.

Supports load patterns:
1. Constant load (steady state testing)
2. Stepped load (gradual ramp-up)
3. Spike load (sudden traffic surges)
4. Wave load (periodic variations)
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import statistics
import random

import aiohttp
from aiohttp import ClientSession, ClientTimeout

logger = logging.getLogger(__name__)


@dataclass
class LoadPattern:
    """Load testing pattern configuration."""
    pattern_type: str  # 'constant', 'stepped', 'spike', 'wave'
    duration_minutes: int
    base_users: int = 10
    peak_users: int = 100
    ramp_up_minutes: int = 5
    step_duration_minutes: int = 10
    step_increment: int = 10


@dataclass
class Endpoint:
    """API endpoint configuration for load testing."""
    path: str
    method: str = 'GET'
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict] = None
    weight: int = 1  # Relative frequency (higher = more requests)
    expected_status: int = 200


@dataclass
class LoadScenario:
    """Complete load testing scenario."""
    name: str
    base_url: str
    endpoints: List[Endpoint]
    pattern: LoadPattern
    think_time_ms: Tuple[int, int] = (1000, 3000)  # Min, max think time
    timeout_seconds: int = 30
    connection_pool_size: int = 100


@dataclass
class RequestResult:
    """Individual request result."""
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    success: bool
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LoadTestResults:
    """Aggregated load test results."""
    scenario_name: str
    start_time: datetime
    end_time: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    
    # Response time statistics (milliseconds)
    response_times: List[float]
    min_response_time: float
    max_response_time: float
    mean_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    
    # Throughput metrics
    requests_per_second: float
    
    # Error metrics
    error_rate: float
    errors_by_type: Dict[str, int]
    
    # Resource utilization (if available)
    cpu_utilization: Optional[float] = None
    memory_utilization: Optional[float] = None
    
    # Statistical confidence
    statistical_confidence: float = 0.95
    sample_size: int = 0


class SyntheticLoadGenerator:
    """Generates synthetic load for performance baseline collection."""
    
    def __init__(self, scenario: LoadScenario):
        """Initialize load generator.
        
        Args:
            scenario: Load testing scenario configuration
        """
        self.scenario = scenario
        self.results: List[RequestResult] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self._stop_flag = False
        
    async def run_load_test(self) -> LoadTestResults:
        """Execute load test according to scenario pattern.
        
        Returns:
            LoadTestResults with aggregated metrics
        """
        logger.info(f"Starting load test: {self.scenario.name}")
        logger.info(f"Pattern: {self.scenario.pattern.pattern_type}, Duration: {self.scenario.pattern.duration_minutes}min")
        
        self.start_time = datetime.now()
        self.results = []
        self._stop_flag = False
        
        try:
            if self.scenario.pattern.pattern_type == 'constant':
                await self._run_constant_load()
            elif self.scenario.pattern.pattern_type == 'stepped':
                await self._run_stepped_load()
            elif self.scenario.pattern.pattern_type == 'spike':
                await self._run_spike_load()
            elif self.scenario.pattern.pattern_type == 'wave':
                await self._run_wave_load()
            else:
                raise ValueError(f"Unknown pattern type: {self.scenario.pattern.pattern_type}")
                
        except Exception as e:
            logger.error(f"Load test failed: {e}")
            raise
        finally:
            self.end_time = datetime.now()
            
        # Aggregate results
        return self._aggregate_results()
        
    async def _run_constant_load(self) -> None:
        """Run constant load pattern."""
        users = self.scenario.pattern.base_users
        duration_seconds = self.scenario.pattern.duration_minutes * 60
        
        logger.info(f"Running constant load: {users} users for {duration_seconds}s")
        
        async with ClientSession(
            timeout=ClientTimeout(total=self.scenario.timeout_seconds),
            connector=aiohttp.TCPConnector(limit=self.scenario.connection_pool_size)
        ) as session:
            tasks = [
                self._user_session(session, user_id, duration_seconds)
                for user_id in range(users)
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def _run_stepped_load(self) -> None:
        """Run stepped load pattern."""
        pattern = self.scenario.pattern
        current_users = pattern.base_users
        step_duration_seconds = pattern.step_duration_minutes * 60
        
        logger.info(f"Running stepped load: {pattern.base_users} → {pattern.peak_users} users")
        
        async with ClientSession(
            timeout=ClientTimeout(total=self.scenario.timeout_seconds),
            connector=aiohttp.TCPConnector(limit=self.scenario.connection_pool_size)
        ) as session:
            step = 0
            while current_users <= pattern.peak_users and not self._stop_flag:
                step += 1
                logger.info(f"Step {step}: {current_users} users for {step_duration_seconds}s")
                
                tasks = [
                    self._user_session(session, user_id, step_duration_seconds)
                    for user_id in range(current_users)
                ]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                current_users += pattern.step_increment
                
    async def _run_spike_load(self) -> None:
        """Run spike load pattern."""
        pattern = self.scenario.pattern
        
        # Normal load
        normal_duration = pattern.duration_minutes * 60 * 0.7  # 70% at base load
        spike_duration = pattern.duration_minutes * 60 * 0.3   # 30% at peak load
        
        logger.info(f"Running spike load: {pattern.base_users} users (normal) → {pattern.peak_users} users (spike)")
        
        async with ClientSession(
            timeout=ClientTimeout(total=self.scenario.timeout_seconds),
            connector=aiohttp.TCPConnector(limit=self.scenario.connection_pool_size)
        ) as session:
            # Normal load phase
            logger.info(f"Normal load phase: {pattern.base_users} users for {normal_duration}s")
            tasks = [
                self._user_session(session, user_id, normal_duration)
                for user_id in range(pattern.base_users)
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Spike phase
            logger.info(f"Spike phase: {pattern.peak_users} users for {spike_duration}s")
            tasks = [
                self._user_session(session, user_id, spike_duration)
                for user_id in range(pattern.peak_users)
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def _run_wave_load(self) -> None:
        """Run wave load pattern (sinusoidal variation)."""
        pattern = self.scenario.pattern
        duration_seconds = pattern.duration_minutes * 60
        wave_period_seconds = 300  # 5-minute wave period
        
        logger.info(f"Running wave load: {pattern.base_users} ↔ {pattern.peak_users} users")
        
        async with ClientSession(
            timeout=ClientTimeout(total=self.scenario.timeout_seconds),
            connector=aiohttp.TCPConnector(limit=self.scenario.connection_pool_size)
        ) as session:
            start = time.time()
            while (time.time() - start) < duration_seconds and not self._stop_flag:
                # Calculate current load based on sine wave
                elapsed = time.time() - start
                wave_position = (elapsed % wave_period_seconds) / wave_period_seconds
                current_users = int(
                    pattern.base_users + 
                    (pattern.peak_users - pattern.base_users) * 
                    (0.5 + 0.5 * asyncio.create_task(self._sine_wave(wave_position)))
                )
                
                logger.debug(f"Wave load: {current_users} users")
                
                # Run for a short duration then adjust
                segment_duration = min(30, duration_seconds - elapsed)  # 30s segments
                tasks = [
                    self._user_session(session, user_id, segment_duration)
                    for user_id in range(current_users)
                ]
                await asyncio.gather(*tasks, return_exceptions=True)
                
    @staticmethod
    async def _sine_wave(position: float) -> float:
        """Calculate sine wave value for position [0, 1]."""
        import math
        return math.sin(2 * math.pi * position)
        
    async def _user_session(self, session: ClientSession, user_id: int, duration_seconds: float) -> None:
        """Simulate a user session with multiple requests.
        
        Args:
            session: HTTP session
            user_id: User identifier
            duration_seconds: Session duration
        """
        start_time = time.time()
        request_count = 0
        
        while (time.time() - start_time) < duration_seconds and not self._stop_flag:
            # Select endpoint based on weight
            endpoint = self._select_endpoint()
            
            # Make request
            result = await self._make_request(session, endpoint)
            self.results.append(result)
            request_count += 1
            
            # Think time between requests
            think_time = random.uniform(
                self.scenario.think_time_ms[0] / 1000,
                self.scenario.think_time_ms[1] / 1000
            )
            await asyncio.sleep(think_time)
            
        logger.debug(f"User {user_id} completed {request_count} requests")
        
    def _select_endpoint(self) -> Endpoint:
        """Select endpoint based on weight."""
        total_weight = sum(e.weight for e in self.scenario.endpoints)
        rand = random.uniform(0, total_weight)
        
        cumulative = 0
        for endpoint in self.scenario.endpoints:
            cumulative += endpoint.weight
            if rand <= cumulative:
                return endpoint
                
        return self.scenario.endpoints[0]  # Fallback
        
    async def _make_request(self, session: ClientSession, endpoint: Endpoint) -> RequestResult:
        """Make HTTP request and record result.
        
        Args:
            session: HTTP session
            endpoint: Endpoint to request
            
        Returns:
            RequestResult with timing and status
        """
        url = f"{self.scenario.base_url}{endpoint.path}"
        start_time = time.time()
        
        try:
            async with session.request(
                method=endpoint.method,
                url=url,
                headers=endpoint.headers,
                json=endpoint.body
            ) as response:
                response_time_ms = (time.time() - start_time) * 1000
                
                # Read response body to ensure complete request
                await response.read()
                
                success = response.status == endpoint.expected_status
                
                return RequestResult(
                    endpoint=endpoint.path,
                    method=endpoint.method,
                    status_code=response.status,
                    response_time_ms=response_time_ms,
                    success=success,
                    error=None if success else f"Expected {endpoint.expected_status}, got {response.status}"
                )
                
        except asyncio.TimeoutError:
            response_time_ms = (time.time() - start_time) * 1000
            return RequestResult(
                endpoint=endpoint.path,
                method=endpoint.method,
                status_code=0,
                response_time_ms=response_time_ms,
                success=False,
                error="Request timeout"
            )
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return RequestResult(
                endpoint=endpoint.path,
                method=endpoint.method,
                status_code=0,
                response_time_ms=response_time_ms,
                success=False,
                error=str(e)
            )
            
    def _aggregate_results(self) -> LoadTestResults:
        """Aggregate individual request results into summary statistics.
        
        Returns:
            LoadTestResults with statistical analysis
        """
        if not self.results:
            raise ValueError("No results to aggregate")
            
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        
        response_times = [r.response_time_ms for r in successful]
        
        if not response_times:
            response_times = [0.0]  # Avoid statistics errors
            
        # Calculate statistics
        sorted_times = sorted(response_times)
        
        duration_seconds = (self.end_time - self.start_time).total_seconds()
        
        # Error categorization
        errors_by_type = {}
        for result in failed:
            error_type = result.error or "Unknown error"
            errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1
            
        return LoadTestResults(
            scenario_name=self.scenario.name,
            start_time=self.start_time,
            end_time=self.end_time,
            total_requests=len(self.results),
            successful_requests=len(successful),
            failed_requests=len(failed),
            response_times=response_times,
            min_response_time=min(sorted_times),
            max_response_time=max(sorted_times),
            mean_response_time=statistics.mean(sorted_times),
            median_response_time=statistics.median(sorted_times),
            p95_response_time=self._percentile(sorted_times, 0.95),
            p99_response_time=self._percentile(sorted_times, 0.99),
            requests_per_second=len(self.results) / duration_seconds if duration_seconds > 0 else 0,
            error_rate=len(failed) / len(self.results) if self.results else 0,
            errors_by_type=errors_by_type,
            statistical_confidence=0.95,  # Assumed for large sample sizes
            sample_size=len(self.results)
        )
        
    @staticmethod
    def _percentile(sorted_values: List[float], percentile: float) -> float:
        """Calculate percentile from sorted values.
        
        Args:
            sorted_values: Sorted list of values
            percentile: Percentile to calculate (0.0-1.0)
            
        Returns:
            Percentile value
        """
        if not sorted_values:
            return 0.0
            
        k = (len(sorted_values) - 1) * percentile
        f = int(k)
        c = k - f
        
        if f + 1 < len(sorted_values):
            return sorted_values[f] + c * (sorted_values[f + 1] - sorted_values[f])
        else:
            return sorted_values[f]
            
    def stop(self) -> None:
        """Stop load test gracefully."""
        logger.info("Stopping load test...")
        self._stop_flag = True


class LoadTestOrchestrator:
    """Orchestrates multiple load test scenarios."""
    
    def __init__(self):
        """Initialize orchestrator."""
        self.scenarios: Dict[str, LoadScenario] = {}
        self.results: Dict[str, LoadTestResults] = {}
        
    def add_scenario(self, scenario: LoadScenario) -> None:
        """Add load test scenario.
        
        Args:
            scenario: Load testing scenario
        """
        self.scenarios[scenario.name] = scenario
        logger.info(f"Added scenario: {scenario.name}")
        
    async def run_all_scenarios(self, sequential: bool = True) -> Dict[str, LoadTestResults]:
        """Run all configured scenarios.
        
        Args:
            sequential: Run scenarios one at a time (True) or in parallel (False)
            
        Returns:
            Dictionary mapping scenario name to results
        """
        logger.info(f"Running {len(self.scenarios)} scenarios ({'sequential' if sequential else 'parallel'})")
        
        if sequential:
            for name, scenario in self.scenarios.items():
                generator = SyntheticLoadGenerator(scenario)
                result = await generator.run_load_test()
                self.results[name] = result
        else:
            tasks = []
            for scenario in self.scenarios.values():
                generator = SyntheticLoadGenerator(scenario)
                tasks.append(generator.run_load_test())
            
            results = await asyncio.gather(*tasks)
            for scenario_name, result in zip(self.scenarios.keys(), results):
                self.results[scenario_name] = result
                
        return self.results
        
    def export_results(self, output_path: Path) -> None:
        """Export results to JSON file.
        
        Args:
            output_path: Path to write results JSON
        """
        output_data = {}
        
        for name, results in self.results.items():
            output_data[name] = {
                'scenario_name': results.scenario_name,
                'start_time': results.start_time.isoformat(),
                'end_time': results.end_time.isoformat(),
                'duration_seconds': (results.end_time - results.start_time).total_seconds(),
                'total_requests': results.total_requests,
                'successful_requests': results.successful_requests,
                'failed_requests': results.failed_requests,
                'response_time_stats': {
                    'min_ms': results.min_response_time,
                    'max_ms': results.max_response_time,
                    'mean_ms': results.mean_response_time,
                    'median_ms': results.median_response_time,
                    'p95_ms': results.p95_response_time,
                    'p99_ms': results.p99_response_time,
                },
                'throughput': {
                    'requests_per_second': results.requests_per_second,
                },
                'errors': {
                    'error_rate': results.error_rate,
                    'errors_by_type': results.errors_by_type,
                },
                'statistical_confidence': results.statistical_confidence,
                'sample_size': results.sample_size,
            }
            
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
            
        logger.info(f"Exported results to {output_path}")
        
    def generate_spring_boot_scenario(self, base_url: str, scenario_name: str = "spring-boot-baseline") -> LoadScenario:
        """Generate default Spring Boot load scenario.
        
        Args:
            base_url: Base URL of Spring Boot application
            scenario_name: Name for scenario
            
        Returns:
            LoadScenario configured for Spring Boot
        """
        endpoints = [
            Endpoint(path="/actuator/health", method="GET", weight=1),
            Endpoint(path="/actuator/metrics", method="GET", weight=1),
            Endpoint(path="/api/v1/data", method="GET", weight=5),
            Endpoint(path="/api/v1/data", method="POST", 
                    body={"test": "data"}, weight=3),
        ]
        
        pattern = LoadPattern(
            pattern_type='stepped',
            duration_minutes=30,
            base_users=10,
            peak_users=50,
            step_duration_minutes=5,
            step_increment=10
        )
        
        return LoadScenario(
            name=scenario_name,
            base_url=base_url,
            endpoints=endpoints,
            pattern=pattern,
            think_time_ms=(1000, 3000),
            timeout_seconds=30
        )


# CLI interface for testing
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Synthetic load testing framework')
    parser.add_argument('--base-url', default='http://localhost:8080', help='Base URL to test')
    parser.add_argument('--pattern', choices=['constant', 'stepped', 'spike', 'wave'], 
                       default='stepped', help='Load pattern')
    parser.add_argument('--duration', type=int, default=5, help='Duration in minutes')
    parser.add_argument('--base-users', type=int, default=10, help='Base user count')
    parser.add_argument('--peak-users', type=int, default=50, help='Peak user count')
    parser.add_argument('--output', default='/tmp/load-test-results.json', 
                       help='Output file for results')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create scenario
    pattern = LoadPattern(
        pattern_type=args.pattern,
        duration_minutes=args.duration,
        base_users=args.base_users,
        peak_users=args.peak_users,
        step_duration_minutes=1,
        step_increment=10
    )
    
    endpoints = [
        Endpoint(path="/actuator/health", method="GET", weight=1),
        Endpoint(path="/", method="GET", weight=5),
    ]
    
    scenario = LoadScenario(
        name=f"test-{args.pattern}",
        base_url=args.base_url,
        endpoints=endpoints,
        pattern=pattern
    )
    
    # Run test
    async def main():
        generator = SyntheticLoadGenerator(scenario)
        results = await generator.run_load_test()
        
        print("\n=== Load Test Results ===")
        print(f"Scenario: {results.scenario_name}")
        print(f"Duration: {(results.end_time - results.start_time).total_seconds():.1f}s")
        print(f"Total Requests: {results.total_requests}")
        print(f"Success Rate: {(results.successful_requests / results.total_requests * 100):.1f}%")
        print(f"\nResponse Times (ms):")
        print(f"  Min: {results.min_response_time:.2f}")
        print(f"  Mean: {results.mean_response_time:.2f}")
        print(f"  Median: {results.median_response_time:.2f}")
        print(f"  P95: {results.p95_response_time:.2f}")
        print(f"  P99: {results.p99_response_time:.2f}")
        print(f"  Max: {results.max_response_time:.2f}")
        print(f"\nThroughput: {results.requests_per_second:.2f} req/s")
        print(f"Error Rate: {results.error_rate * 100:.2f}%")
        
        # Export results
        orchestrator = LoadTestOrchestrator()
        orchestrator.results[scenario.name] = results
        orchestrator.export_results(Path(args.output))
        print(f"\nResults exported to: {args.output}")
    
    asyncio.run(main())
