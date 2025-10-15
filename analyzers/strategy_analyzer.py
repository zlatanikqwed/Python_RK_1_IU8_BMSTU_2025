"""
@file strategy_analyzer.py
@brief Calculation of the optimal budget = (sum of department 26 allocations in ACTIVE + PLANNING projects) + 500_000.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd

from analyzers.base_rnd_analyzer import BaseAnalyzer
from config.messages import HEAD_STRATEGY, LogMsg
from config.enums import Thresholds


class StrategyAnalyzer(BaseAnalyzer):
    """
    @class StrategyAnalyzer
    @brief Builds the strategy section for department 26 using company.json.
    """

    def execute_analysis(self) -> Dict[str, Any]:
        """
        @brief Run the strategy pipeline and compute optimal budget + KPIs.
        @return Dict with title, success criteria, optimal budget breakdown, current budget,
                gap, KPI summary and monitoring metric list.
        """
        self.logger.info(LogMsg.ANALYSIS_START.format("Development Strategy - dept=26 (allocation-based, simplified)"))

        prj_all = self.projects_df()
        df = self._projects_with_dept26_alloc(prj_all)  # all projects where dept 26 participates

        current_budget = self._department_budget(self.department_id)

        # Allocation sums by status (planning, active, completed, all)
        breakdown_status = self._budget_breakdown_by_status(df)

        # Minimal working budget = planning + active
        min_budget = float(breakdown_status["planning"] + breakdown_status["active"])

        # Fixed reserve 500_000 
        reserve_fixed = float(getattr(Thresholds, "FIXED_RESERVE", 500_000))

        # Final optimal budget = min + fixed reserve
        final_optimal = float(min_budget + reserve_fixed)

        # Department-level KPIs
        kpis = self._compute_kpis_for_dept26(df)

        success_criteria = [
            "Project completed: is_completed=True / status='completed'",
            "Valid department 26 allocation: budget_allocation > 0.",
        ]

        result = {
            "title": HEAD_STRATEGY,
            "success_criteria": success_criteria,
            "optimal_budget_rub": float(round(final_optimal, 2)),
            "optimal_budget_breakdown": {
                "planning": float(breakdown_status["planning"]),
                "active": float(breakdown_status["active"]),
                "completed": float(breakdown_status["completed"]),
                "min": float(round(min_budget, 2)),          # planning + active
                "reserve_fixed": float(round(reserve_fixed, 2)),
                "final": float(round(final_optimal, 2)),     # min + reserve
                "all": float(breakdown_status["all"]),       # planning + active + completed
            },
            "current_budget_rub": float(current_budget) if current_budget is not None else None,
            "budget_gap_rub": float(round(final_optimal - current_budget, 2)) if current_budget is not None else None,
            "kpi_summary": kpis,
            "monitoring_metrics": self._monitoring_metric_list(),
        }

        self.logger.info(LogMsg.ANALYSIS_COMPLETE.format("Development Strategy - dept=26 (allocation-based, simplified)"))
        return result

    def print(self, result: Dict[str, Any]) -> str:
        """
        @brief Render a text section from the result dict.
        @param result Output of execute_analysis()
        @return Formatted multiline string
        """
        lines: List[str] = []

        bk = result.get("optimal_budget_breakdown", {})
        cb = result.get("current_budget_rub")
        gap = result.get("budget_gap_rub")

        lines.append("Optimal Budget for Department 26:")
        lines.append(f"  * planning:          {bk.get('planning', 0.0):,.0f}")
        lines.append(f"  * active:            {bk.get('active', 0.0):,.0f}")
        lines.append(f"  * completed:         {bk.get('completed', 0.0):,.0f}")
        lines.append(f"  * min (planning+active):     {bk.get('min', 0.0):,.0f}")
        lines.append(f"  * reserve (fixed):           {bk.get('reserve_fixed', 0.0):,.0f}")
        lines.append(f"  * final (min + reserve):     {bk.get('final', 0.0):,.0f}")
        lines.append(f"  * all (planning+active+completed): {bk.get('all', 0.0):,.0f}")

        if cb is not None:
            lines.append(f"\nCurrent budget of department 26:        {cb:,.0f}")
        if gap is not None:
            sign = "+" if gap >= 0 else "-"
            lines.append(f"Gap (final - current):                 {sign}{abs(gap):,.0f}")

        lines.append("\nSuccess criteria:")
        for i, c in enumerate(result.get("success_criteria", []), 1):
            lines.append(f"  {i}. {c}")

        k = result.get("kpi_summary", {})
        if k:
            lines.append("\nDepartment 26 KPIs (by participation share):")
            lines.append(f"  * Projects with 26:                    {k.get('projects_total', 0)}")
            lines.append(f"  * Aggregate ROI:                       {k.get('roi_agg_26', 0.0):.3f}")
            lines.append(f"  * Average ROI:                         {k.get('roi_avg_26', 0.0):.3f}")
            lines.append(f"  * Success rate (completed), %:         {k.get('success_rate_pct', 0.0):.1f}%")
            pb = k.get("payback_median_days_26")
            lines.append(f"  * Median payback (days):               {pb if pb is not None else '-'}")
            lines.append(f"  * Budget utilization (avg), %:         {k.get('utilization_avg_pct_26', 0.0):.1f}%")

        lines.append("\nMonitoring metric system:")
        for i, m in enumerate(result.get("monitoring_metrics", []), 1):
            lines.append(f"  {i}. {m}")

        return "\n".join(lines)

    def _projects_with_dept26_alloc(self, prj: pd.DataFrame) -> pd.DataFrame:
        """
        @brief Only projects where department 26 participates and extract.
        @param prj Raw projects DataFrame from BaseAnalyzer
        @return Filtered DataFrame with department-26 allocations
        """
        if prj is None or prj.empty:
            return pd.DataFrame()

        df = prj.copy()

        # Extract allocations for 26 and total
        def allocs_26_and_total(lst) -> Tuple[float, float]:
            """
            @brief Parse participating_departments list to get both dept26 and total allocations.
            @param lst Raw list of participants
            @return (dept26_alloc, total_alloc) or (NaN, NaN)
            """
            if not isinstance(lst, list):
                return (np.nan, np.nan)
            my, total, has_my = 0.0, 0.0, False
            for it in lst:
                if not isinstance(it, dict):
                    continue
                try:
                    alloc = float(it.get("budget_allocation") or 0.0)
                except Exception:
                    alloc = 0.0
                total += alloc
                try:
                    if int(it.get("department_id")) == 26:
                        my += alloc
                        has_my = True
                except Exception:
                    pass
            return (my if has_my and my > 0 else np.nan, total if total > 0 else np.nan)

        df[["dept26_alloc", "total_alloc"]] = df["participating_departments"].apply(
            lambda x: pd.Series(allocs_26_and_total(x))
        )
        has_26 = df["dept26_alloc"].notna()

        out = df.loc[has_26].copy()

        # Normalize numeric fields
        for col in ["budget", "actual_cost", "profit", "roi_pct", "duration_days",
                    "dept26_alloc", "total_alloc"]:
            out[col] = pd.to_numeric(out.get(col), errors="coerce")

        # Participation share
        out["share26"] = np.where(out["total_alloc"] > 0, out["dept26_alloc"] / out["total_alloc"], np.nan)

        # Completion normalization (any indicator works)
        out["is_completed"] = (
            out.get("is_completed", False).fillna(False).astype(bool)
            | out.get("status", "").astype(str).str.lower().eq("completed")
            | (pd.to_numeric(out.get("completion_percentage", 0), errors="coerce") >= 100)
        )

        # Profit portion of 26
        out["profit26"] = out["profit"] * out["share26"]

        return out

    def _budget_breakdown_by_status(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        @brief Sum of department 26 allocations by project status:
               planning / active / completed / all.
        @param df Projects with dept 26 allocations
        @return Dict with amounts per status
        """
        res = {"planning": 0.0, "active": 0.0, "completed": 0.0, "all": 0.0}
        if df is None or df.empty:
            return res

        d = df.copy()
        d["dept26_alloc"] = pd.to_numeric(d["dept26_alloc"], errors="coerce")

        # Completion and status masks
        is_completed = d["is_completed"]
        status_l = d.get("status", "").astype(str).str.lower()
        planning_set = {"planning", "planned", "plan", "scheduled", "in_planning"}
        active_set   = {"active", "in_progress", "ongoing", "working", "execution", "running"}

        is_planning = status_l.isin(planning_set) & (~is_completed)
        is_active   = status_l.isin(active_set) & (~is_completed)

        res["completed"] = float(d.loc[is_completed, "dept26_alloc"].dropna().sum())
        res["active"]    = float(d.loc[is_active,    "dept26_alloc"].dropna().sum())
        res["planning"]  = float(d.loc[is_planning,  "dept26_alloc"].dropna().sum())
        res["all"]       = res["completed"] + res["active"] + res["planning"]
        return res

    def _compute_kpis_for_dept26(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        @brief Compute KPIs for department 26 by participation share.
        @param df Projects with dept 26 participation
        @return Dict with KPI aggregates
        """
        if df is None or df.empty:
            return {
                "projects_total": 0,
                "roi_agg_26": 0.0,
                "roi_avg_26": 0.0,
                "success_rate_pct": 0.0,
                "payback_median_days_26": None,
                "utilization_avg_pct_26": 0.0,
            }

        # ROI for 26 
        roi26 = pd.Series(np.nan, index=df.index)
        mask = (df["dept26_alloc"] > 0) & df["profit26"].notna()
        roi26.loc[mask] = df.loc[mask, "profit26"] / df.loc[mask, "dept26_alloc"]
        roi_avg_26 = float(roi26.dropna().mean()) if roi26.notna().any() else 0.0

        cost_sum_26 = float(df["dept26_alloc"].fillna(0).sum())
        profit_sum_26 = float(df["profit26"].fillna(0).sum())
        roi_agg_26 = float(profit_sum_26 / cost_sum_26) if cost_sum_26 > 0 else 0.0

        success_rate = float(df["is_completed"].mean() * 100.0) if len(df) else 0.0

        daily_profit_26 = df["profit26"] / df["duration_days"].replace(0, np.nan)
        payback_26 = np.where(
            (df["dept26_alloc"] > 0) & (daily_profit_26.notna()) & (daily_profit_26 > 0),
            df["dept26_alloc"] / daily_profit_26,
            np.nan,
        )
        payback_med_26 = float(pd.Series(payback_26).dropna().median()) if np.isfinite(payback_26).any() else None

        actual26 = np.where(df["actual_cost"].notna(), df["actual_cost"] * df["share26"], np.nan)
        plan26 = df["budget"] * df["share26"]
        util = np.where((~np.isnan(actual26)) & (plan26 > 0), (actual26 / plan26) * 100.0, np.nan)
        util_avg = float(pd.Series(util).dropna().mean()) if np.isfinite(util).any() else 0.0

        return {
            "projects_total": int(len(df)),
            "roi_agg_26": round(roi_agg_26, 4),
            "roi_avg_26": round(roi_avg_26, 4),
            "success_rate_pct": round(success_rate, 1),
            "payback_median_days_26": round(payback_med_26, 1) if isinstance(payback_med_26, (int, float)) else None,
            "utilization_avg_pct_26": round(util_avg, 1),
        }

    def _department_budget(self, department_id: int) -> Optional[float]:
        """
        @brief Read current budget of a department.
        @param department_id Department id
        @return Budget as float or None if missing
        """
        try:
            for d in (self.raw.departments or []):
                if int(d.get("id")) == int(department_id):
                    val = d.get("budget")
                    return float(val) if val is not None else None
        except Exception:
            return None
        return None

    def _monitoring_metric_list(self) -> List[str]:
        """
        @brief Canonical metric set for monthly innovation monitoring.
        @return List of KPI names
        """
        return [
            "Aggregate ROI, T4Q.",
            "Average ROI.",
            "Median payback (days).",
            "Success rate (completed), %.",
            "Budget utilization (actual/plan), %.",
            "Average duration (duration_days).",
            "Collaboration rate (joint projects), %.",
        ]
