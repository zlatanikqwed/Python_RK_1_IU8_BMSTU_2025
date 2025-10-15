"""
@file base_rnd_analyzer.py
@brief Core loader & normalizer (R&D department).
       Loads JSON once, prepares DataFrames for employees and projects.
"""

from typing import Any, Dict, List, Optional, Iterable
from dataclasses import dataclass
import json
import math
from datetime import datetime
import pandas as pd
import numpy as np

# Configuration and types
from config.enums import (
    Degree, DEGREE_ORDER, DEGREE_MAP_RU,
    ProjectStatus, ProjectType, Thresholds
)
from utilits.logger import analysis_logger


@dataclass
class LoadResult:
    """@brief Container for JSON sections."""
    metadata: Dict[str, Any]
    departments: List[Dict[str, Any]]
    employees: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    equipment: List[Dict[str, Any]]


class BaseAnalyzer:
    """
    @brief Base class for all analyzers.
    @param json_path Path to company.json
    @param department_id Target department id (default 26 - R&D)
    @throws FileNotFoundError, json.JSONDecodeError on read/parse issues
    """

    def __init__(self, json_path: str, department_id: 26) -> None:
        self.json_path = json_path
        self.department_id = department_id
        self.logger = analysis_logger.get_logger(self.__class__.__name__)
        self.logger.info("Initializing BaseAnalyzer")

        raw = self._load_json(json_path)
        self.raw = raw

        # Prepare DataFrames for subclasses
        self.employees_df_ = self._build_employees_df(raw.employees, department_id)
        self.projects_df_  = self._build_projects_df(raw.projects, department_id)

        self.logger.info(
            f"DF ready: employees={len(self.employees_df_)} rows; projects={len(self.projects_df_)} rows"
        )


    def employees_df(self) -> pd.DataFrame:
        """
        @brief Normalized employees DataFrame for department.
        @return pd.DataFrame
        """
        return self.employees_df_.copy()

    def projects_df(self) -> pd.DataFrame:
        """
        @brief Normalized projects DataFrame with participation of department.
        @return pd.DataFrame
        """
        return self.projects_df_.copy()

    def _load_json(self, path: str) -> LoadResult:
        """
        @brief Read company.json and return a structured LoadResult.
        @param path 
        @return LoadResult
        """
        self.logger.info("Starting JSON load")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        metadata    = data.get("metadata", {}) or {}
        departments = data.get("departments", []) or []
        employees   = data.get("employees", []) or []
        projects    = data.get("projects", []) or []
        equipment   = data.get("equipment", []) or []

        self.logger.info(
            f"JSON loaded: meta={bool(metadata)}, dep={len(departments)}, "
            f"emp={len(employees)}, proj={len(projects)}, eq={len(equipment)}"
        )

        return LoadResult(metadata, departments, employees, projects, equipment)

    def _build_employees_df(self, employees: List[Dict[str, Any]], dep_id: int) -> pd.DataFrame:
        """
        @brief Build employees DataFrame.
        @param employees from JSON
        @param dep_id Department filter
        @return Normalized pd.DataFrame
        """
        rows = []
        for e in employees:
            wi = e.get("work_info", {}) or {}
            if wi.get("department_id") != dep_id:
                continue

            pi = e.get("personal_info", {}) or {}
            ai = e.get("additional_info", {}) or {}

            full_name = (
                pi.get("full_name")
                or " ".join(filter(None, [pi.get("last_name"), pi.get("first_name"), pi.get("middle_name")]))
            ).strip()

            degree_raw = ai.get("education")
            degree = self._normalize_degree(degree_raw)

            skills = wi.get("skills") or []
            if not isinstance(skills, list):
                skills = [skills]

            langs = ai.get("language_skills") or []
            if not isinstance(langs, list):
                langs = [langs]

            salary = self._to_float(wi.get("salary"))
            perf   = self._to_float(wi.get("performance_score"))
            exp    = self._to_int(wi.get("experience_years"))
            certs  = self._to_int(ai.get("certifications"))
            hire   = self._to_datetime(wi.get("hire_date"))

            rows.append({
                "employee_id": e.get("employee_id"),
                "full_name": full_name,
                "position": wi.get("position"),
                "salary": salary,
                "hire_date": hire,
                "experience_years": exp,
                "performance_score": perf,
                "skills": skills,
                "is_team_lead": bool(wi.get("is_team_lead", False)),
                "work_schedule": wi.get("work_schedule"),
                "degree_raw": degree_raw,
                "degree": degree,
                "certifications": certs,
                "language_skills": langs,
                "security_clearance": bool(ai.get("security_clearance", False)),
            })

        df = pd.DataFrame(rows)
        # sort by performance
        if not df.empty and "performance_score" in df.columns:
            df = df.sort_values("performance_score", ascending=False).reset_index(drop=True)

        self.logger.info(f"Employees DF built: {len(df)} rows for department_id={dep_id}")
        return df

    def _build_projects_df(self, projects: List[Dict[str, Any]], dep_id: int) -> pd.DataFrame:
        """
        @brief Build projects DataFrame where 26.
        @param projects  from JSON
        @param dep_id 
        @return Normalized pd.DataFrame
        """
        rows = []
        for p in projects:
            parts = p.get("participating_departments") or []
            part_ids = [i.get("department_id") for i in parts if isinstance(i, dict)]
            if dep_id not in part_ids:
                continue

            timeline   = p.get("timeline", {}) or {}
            financials = p.get("financials", {}) or {}
            metrics    = p.get("metrics", {}) or {}

            start = self._to_datetime(timeline.get("start_date"))
            end   = self._to_datetime(timeline.get("end_date"))
            dur   = self._to_int(timeline.get("duration_days"))

            if dur is None and start and end:
                dur = (end - start).days

            budget      = self._to_float(financials.get("budget"))
            actual_cost = self._to_float(financials.get("actual_cost"))
            profit      = self._to_float(financials.get("profit"))
            roi_pct     = self._to_float(financials.get("roi_percentage"))

            if roi_pct is not None:
                roi_ratio = roi_pct / 100.0
            elif (budget is not None and budget > 0 and profit is not None):
                roi_ratio = profit / budget
            else:
                roi_ratio = None

            rows.append({
                "project_id": p.get("project_id"),
                "name": p.get("name"),
                "type": p.get("type") or p.get("project_type"), 
                "status": p.get("status"),
                "start_date": start,
                "end_date": end,
                "duration_days": dur,
                "budget": budget,
                "actual_cost": actual_cost,
                "profit": profit,
                "roi_ratio": roi_ratio,
                "roi_pct": roi_pct,
                "completion_percentage": self._to_int(metrics.get("completion_percentage")),
                "risk_level": metrics.get("risk_level"),
                "priority": metrics.get("priority"),
                "participating_departments": parts,
            })

        df = pd.DataFrame(rows)
        if not df.empty:
            df["is_completed"] = df["status"].astype(str).str.lower().eq(ProjectStatus.COMPLETED.value)

        self.logger.info(f"Projects DF built: {len(df)} rows with department_id={dep_id} participation")
        return df

    def _normalize_degree(self, value: Any) -> str:
        """
        @brief Normalize education (RU/EN - canonical Degree).
        @param value Raw string 
        @return one of: ['dsc','phd','master','bachelor','none','other']
        """
        if value is None:
            return Degree.NONE.value
        s = str(value).strip().lower()
        if s in DEGREE_MAP_RU:
            return DEGREE_MAP_RU[s]
        # Recognize simple English tokens
        if s in ("phd", "msc", "master", "bachelor", "bs", "ms"):
            return {
                "phd": Degree.PHD.value,
                "msc": Degree.MASTER.value,
                "master": Degree.MASTER.value,
                "ms": Degree.MASTER.value,
                "bachelor": Degree.BACHELOR.value,
                "bs": Degree.BACHELOR.value,
            }[s]
        return Degree.OTHER.value

    def _to_datetime(self, v: Any) -> Optional[datetime]:
        """
        @brief Parse date/datetime (ISO-like strings). Return None on failure.
        """
        if v in (None, "", float("nan")):
            return None
        try:
            return pd.to_datetime(v, errors="coerce")
        except Exception:
            try:
                return pd.to_datetime(str(v), errors="coerce")
            except Exception:
                return None

    def _to_float(self, v: Any) -> Optional[float]:
        """
        @brief Safely cast to float. Return None if not possible.
        """
        try:
            if v is None or (isinstance(v, float) and math.isnan(v)):
                return None
            return float(v)
        except Exception:
            return None

    def _to_int(self, v: Any) -> Optional[int]:
        """
        @brief Safely cast to int. Return None if not possible.
        """
        try:
            if v is None or (isinstance(v, float) and math.isnan(v)):
                return None
            return int(v)
        except Exception:
            return None

    @staticmethod
    def safe_mean(series: pd.Series, default: float = 0.0) -> float:
        """
        @brief Mean with safe NaN/empty handling.
        """
        if series is None:
            return float(default)
        s = series.dropna()
        return float(s.mean()) if len(s) else float(default)

    @staticmethod
    def safe_sum(series: pd.Series, default: float = 0.0) -> float:
        """
        @brief Sum with safe NaN/empty handling.
        """
        if series is None:
            return float(default)
        s = series.dropna()
        return float(s.sum()) if len(s) else float(default)
