"""
State introspection and self-monitoring for SDLC Agent workflow.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
import json
from collections import defaultdict

from src.LLMS.groq_llm import get_llm

def parse_datetime(datetime_str: str) -> datetime:
    """
    Parse datetime string to datetime object.
    
    Args:
        datetime_str (str): Datetime string
        
    Returns:
        datetime: Parsed datetime object
    """
    try:
        return datetime.fromisoformat(datetime_str)
    except ValueError:
        # If parsing fails, return current time
        return datetime.now()

def analyze_workflow_efficiency(phase_times: Dict[str, float]) -> Dict[str, Any]:
    """
    Analyze workflow efficiency based on time spent in each phase.
    
    Args:
        phase_times (Dict[str, float]): Time spent in each phase in seconds
        
    Returns:
        Dict[str, Any]: Analysis results
    """
    total_time = sum(phase_times.values())
    phase_percentages = {phase: (time / total_time) * 100 for phase, time in phase_times.items()}
    
    # Identify bottlenecks (phases taking more than 30% of total time)
    bottlenecks = [phase for phase, percentage in phase_percentages.items() if percentage > 30]
    
    # Calculate efficiency score
    # Lower score is better, indicating more balanced time distribution
    time_variance = sum((percentage - (100 / len(phase_times))) ** 2 for percentage in phase_percentages.values())
    efficiency_score = time_variance / len(phase_times)
    
    return {
        "total_time_seconds": total_time,
        "phase_percentages": phase_percentages,
        "bottlenecks": bottlenecks,
        "efficiency_score": efficiency_score,
        "balanced": efficiency_score < 400  # Threshold for considering workflow balanced
    }

def monitor_workflow_progress(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Self-monitoring node to analyze workflow progress.
    
    Args:
        state (Dict[str, Any]): Current workflow state
        
    Returns:
        Dict[str, Any]: Updated state with monitoring data
    """
    current_stage = state.get("current_stage", "")
    history = state.get("history", [])
    
    # Calculate time spent in each phase
    phase_times = defaultdict(float)
    
    if len(history) > 1:
        for i in range(1, len(history)):
            phase = history[i-1].get("stage", "UNKNOWN")
            start_time = parse_datetime(history[i-1].get("timestamp", datetime.now().isoformat()))
            end_time = parse_datetime(history[i].get("timestamp", datetime.now().isoformat()))
            
            time_diff = (end_time - start_time).total_seconds()
            phase_times[phase] += time_diff
    
    # Add current phase time
    if history:
        last_stage = history[-1].get("stage", "UNKNOWN")
        start_time = parse_datetime(history[-1].get("timestamp", datetime.now().isoformat()))
        current_time = datetime.now()
        
        time_diff = (current_time - start_time).total_seconds()
        phase_times[last_stage] += time_diff
    
    # Analyze workflow efficiency
    analysis = analyze_workflow_efficiency(dict(phase_times))
    
    # Generate insights using LLM
    if history and len(phase_times) > 1:
        prompt = f"""
        You are an AI workflow efficiency expert. Analyze the following data about an SDLC workflow:
        
        Current stage: {current_stage}
        
        Time spent in each phase (seconds):
        {json.dumps(dict(phase_times), indent=2)}
        
        Efficiency analysis:
        {json.dumps(analysis, indent=2)}
        
        History summary:
        {json.dumps([{"stage": h.get("stage"), "timestamp": h.get("timestamp")} for h in history[-5:]], indent=2)}
        
        Provide 3-5 concise, actionable insights to improve workflow efficiency.
        Format each insight as a bullet point.
        """
        
        llm = get_llm(temperature=0.7)
        insights = llm.invoke(prompt)
    else:
        insights = "Not enough data to generate meaningful insights yet."
    
    # Update state with monitoring data
    new_state = state.copy()
    new_state["monitoring"] = {
        "phase_times": dict(phase_times),
        "efficiency_analysis": analysis,
        "bottlenecks": analysis.get("bottlenecks", []),
        "insights": insights,
        "last_monitored": datetime.now().isoformat()
    }
    
    return new_state

def get_monitoring_summary(state: Dict[str, Any]) -> str:
    """
    Get a human-readable summary of monitoring data.
    
    Args:
        state (Dict[str, Any]): Current workflow state
        
    Returns:
        str: Monitoring summary in markdown format
    """
    monitoring_data = state.get("monitoring", {})
    
    if not monitoring_data:
        return "No monitoring data available yet."
    
    phase_times = monitoring_data.get("phase_times", {})
    analysis = monitoring_data.get("efficiency_analysis", {})
    bottlenecks = monitoring_data.get("bottlenecks", [])
    insights = monitoring_data.get("insights", "No insights available.")
    
    # Format time spent in each phase
    phase_time_str = "\n".join([f"- **{phase}**: {time:.2f} seconds" for phase, time in phase_times.items()])
    
    # Format bottlenecks
    if bottlenecks:
        bottleneck_str = "\n".join([f"- {bottleneck}" for bottleneck in bottlenecks])
    else:
        bottleneck_str = "No bottlenecks detected."
    
    summary = f"""
    ## Workflow Monitoring Summary
    
    ### Time Spent by Phase
    {phase_time_str}
    
    ### Efficiency Score
    {analysis.get("efficiency_score", 0):.2f} (lower is better)
    
    ### Bottlenecks
    {bottleneck_str}
    
    ### Insights
    {insights}
    
    _Last updated: {monitoring_data.get("last_monitored", "Unknown")}_
    """
    
    return summary