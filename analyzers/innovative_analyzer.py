"""
@file innovative_analyzer.py
@brief R&D vs Commercial points across the whole company.
       Computes project ROI, builds R&D (deps {26,27,28,29,30}) and Commercial (deps {17,18,19,20}),
       compares by average ROI, and estimates typical payback for R&D.
"""

from typing import Dict, Any, Iterable, Set, List
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from analyzers.base_rnd_analyzer import BaseAnalyzer
from config.messages import HEAD_INNOVATION, ReportMsg, LogMsg


# Description of departments by id
RESEARCH_DEPS: Set[int]   = {26, 27, 28, 29, 30}
COMMERCIAL_DEPS: Set[int] = {17, 18, 19, 20}


class InnovativeAnalyzer(BaseAnalyzer):
    """
    @class InnovativeAnalyzer
    @brief Computes company-wide “Innovation Effectiveness”:
           - overall ROI for all research projects,
           - comparison of R&D vs Commercial cohorts,
           - typical R&D payback (median payback_days).
    """

    def execute_analysis(self) -> Dict[str, Any]:
        """
        @brief Run the R&D vs Commercial effectiveness pipeline on all projects.
        @return dict
        """
        self.logger.info(LogMsg.ANALYSIS_START.format("Innovation Effectiveness"))

        df = self._projects_df()
        if df.empty:
            empty_tbl = pd.DataFrame(columns=[
                "project_id","name","status","duration_days","budget","actual_cost","profit",
                "roi_ratio","roi_pct","payback_days","is_research","is_commercial"
            ])
            empty_summary = pd.DataFrame(columns=[
                "type","projects","avg_roi_ratio","avg_roi_pct",
                "overall_roi_ratio","overall_roi_pct",
                "median_payback_days","success_rate_pct","profit_sum","cost_sum"
            ])
            return {
                "title": HEAD_INNOVATION,
                "roi_by_project": empty_tbl,
                "cohort_summary": empty_summary,
                "overall_roi_research": 0.0,
                "overall_roi_commercial": 0.0,
                "typical_payback_research_days": None,
            }

        rnd_df  = df[df["is_research"]].copy()
        comm_df = df[df["is_commercial"]].copy()

        rnd_summary  = self._cohort_summary(rnd_df)
        comm_summary = self._cohort_summary(comm_df)

        cohort_summary_df = pd.DataFrame([
            {"type": "R&D", "projects": rnd_summary["projects"],
             "avg_roi_ratio": rnd_summary["avg_roi_ratio"],
             "avg_roi_pct": rnd_summary["avg_roi_pct"],
             "overall_roi_ratio": rnd_summary["overall_roi_ratio"],
             "overall_roi_pct": rnd_summary["overall_roi_pct"],
             "median_payback_days": rnd_summary["median_payback_days"],
             "success_rate_pct": rnd_summary["success_rate_pct"],
             "profit_sum": rnd_summary["profit_sum"], "cost_sum": rnd_summary["cost_sum"]},
            {"type": "Commercial", "projects": comm_summary["projects"],
             "avg_roi_ratio": comm_summary["avg_roi_ratio"],
             "avg_roi_pct": comm_summary["avg_roi_pct"],
             "overall_roi_ratio": comm_summary["overall_roi_ratio"],
             "overall_roi_pct": comm_summary["overall_roi_pct"],
             "median_payback_days": comm_summary["median_payback_days"],
             "success_rate_pct": comm_summary["success_rate_pct"],
             "profit_sum": comm_summary["profit_sum"], "cost_sum": comm_summary["cost_sum"]},
        ])[["type","projects","avg_roi_ratio","avg_roi_pct",
            "overall_roi_ratio","overall_roi_pct",
            "median_payback_days","success_rate_pct","profit_sum","cost_sum"]]

        result = {
            "title": HEAD_INNOVATION,
            "roi_by_project": df.loc[:, [
                "project_id","name","status","duration_days","budget","actual_cost","profit",
                "roi_ratio","roi_pct","payback_days","is_research","is_commercial"
            ]].sort_values(["roi_ratio","roi_pct"], ascending=[False, False], na_position="last").reset_index(drop=True),
            "cohort_summary": cohort_summary_df,
            "overall_roi_research": round(rnd_summary["overall_roi_ratio"], 4) if np.isfinite(rnd_summary["overall_roi_ratio"]) else 0.0,
            "overall_roi_commercial": round(comm_summary["overall_roi_ratio"], 4) if np.isfinite(comm_summary["overall_roi_ratio"]) else 0.0,
            "typical_payback_research_days": round(rnd_summary["median_payback_days"], 1) if np.isfinite(rnd_summary["median_payback_days"]) else None,
        }

        self.logger.info(LogMsg.ANALYSIS_COMPLETE.format("Innovation Effectiveness (global cohorts)"))
        return result

    def print(self, result: Dict[str, Any]) -> str:
        """
        @brief Convert analysis result dict to a readable section.
        @param result Output from execute_analysis()
        @return str formatted section suitable for console
        """
        lines: List[str] = []
        lines.append(ReportMsg.ROI_RND.format(result.get("overall_roi_research", 0.0)))
        lines.append(ReportMsg.ROI_COMM.format(result.get("overall_roi_commercial", 0.0)))
        lines.append(f"Typical R&D payback (median): {result.get('typical_payback_research_days')} days")

        summary = result.get("cohort_summary")
        if isinstance(summary, pd.DataFrame) and not summary.empty:
            lines.append("\nSummary (aggregate & average):")
            for _, r in summary.iterrows():
                lines.append(
                    f"  • {r['type']}: n={int(r['projects'])}, "
                    f"avg ROI={r['avg_roi_ratio']:.3f} ({r['avg_roi_pct']:.1f}%), "
                    f"overall ROI={r['overall_roi_ratio']:.3f} ({r['overall_roi_pct']:.1f}%), "
                    f"payback~{r['median_payback_days']:.1f} days, "
                    f"success={r['success_rate_pct']:.1f}%"
                )
        return "\n".join(lines)

    #Plots

    def plot_cohort_roi_bars(self, result: Dict[str, Any], out_dir: str = "plots") -> str:
        """
        @brief Save grouped bars for average vs overall ROI by cohort (R&D, Commercial).
        @param result  Dict from execute_analysis()
        @param out_dir Output directory
        @return str path to saved PNG
        """
        self._ensure_dir(out_dir)
        summary = result.get("cohort_summary")
        if not isinstance(summary, pd.DataFrame) or summary.empty:
            return os.path.join(out_dir, "innovation_cohort_roi_bars.png")

        x = summary["type"]
        avg = summary["avg_roi_ratio"]
        ovl = summary["overall_roi_ratio"]

        plt.figure()
        width = 0.35
        idx = np.arange(len(x))
        plt.bar(idx - width/2, avg, width, label="Average ROI")
        plt.bar(idx + width/2, ovl, width, label="Overall ROI")
        plt.xticks(idx, x)
        plt.ylabel("ROI (ratio)")
        plt.title("R&D vs Commercial - ROI (average vs overall)")
        plt.legend()
        path = os.path.join(out_dir, "innovation_cohort_roi_bars.png")
        plt.tight_layout()
        plt.savefig(path, dpi=130)
        plt.close()
        return path

    def plot_roi_hist_by_cohort(self, out_dir: str = "plots", bins: int = 10) -> str:
        """
        @brief Save overlaid histograms of per-project ROI for R&D and Commercial cohorts.
        @param out_dir Output directory
        @param bins    Histogram bins
        @return str path to saved PNG
        """
        self._ensure_dir(out_dir)
        df = self._projects_df()
        rnd = pd.to_numeric(df.loc[df["is_research"], "roi_ratio"], errors="coerce").dropna()
        com = pd.to_numeric(df.loc[df["is_commercial"], "roi_ratio"], errors="coerce").dropna()

        plt.figure()
        plt.hist(rnd, bins=bins, alpha=0.6, label="R&D")
        plt.hist(com, bins=bins, alpha=0.6, label="Commercial")
        plt.xlabel("ROI (ratio)")
        plt.ylabel("Projects")
        plt.title("Per-project ROI distribution by cohort")
        plt.legend()
        path = os.path.join(out_dir, "innovation_roi_hist.png")
        plt.tight_layout()
        plt.savefig(path, dpi=130)
        plt.close()
        return path

    def plot_payback_hist_rnd(self, out_dir: str = "plots", bins: int = 10) -> str:
        """
        @brief Save histogram of payback (days) for R&D projects only.
        @param out_dir Output directory
        @param bins    Histogram bins
        @return str path to saved PNG
        """
        self._ensure_dir(out_dir)
        df = self._projects_df()
        pay = pd.to_numeric(df.loc[df["is_research"], "payback_days"], errors="coerce").dropna()

        plt.figure()
        plt.hist(pay, bins=bins)
        plt.xlabel("Payback, days")
        plt.ylabel("Projects")
        plt.title("R&D - Payback distribution")
        path = os.path.join(out_dir, "innovation_rnd_payback_hist.png")
        plt.tight_layout()
        plt.savefig(path, dpi=130)
        plt.close()
        return path

    def plot_roi_vs_duration_scatter(self, out_dir: str = "plots") -> str:
        """
        @brief Save scatter plot ROI vs duration (days), colored by cohort.
        @param out_dir Output directory
        @return str path to saved PNG
        """
        self._ensure_dir(out_dir)
        df = self._projects_df().copy()
        df["roi_ratio"] = pd.to_numeric(df["roi_ratio"], errors="coerce")
        df["duration_days"] = pd.to_numeric(df["duration_days"], errors="coerce")

        plt.figure()
        plt.scatter(df.loc[df["is_research"], "duration_days"],
                    df.loc[df["is_research"], "roi_ratio"], alpha=0.8, label="R&D")
        plt.scatter(df.loc[df["is_commercial"], "duration_days"],
                    df.loc[df["is_commercial"], "roi_ratio"], alpha=0.8, label="Commercial")
        plt.xlabel("Duration, days")
        plt.ylabel("ROI (ratio)")
        plt.title("ROI vs Duration by cohort")
        plt.legend()
        path = os.path.join(out_dir, "innovation_scatter_roi_duration.png")
        plt.tight_layout()
        plt.savefig(path, dpi=130)
        plt.close()
        return path


    def _projects_df(self) -> pd.DataFrame:
        """
        @brief Build project DataFrame from raw JSON with cohort flags and ROI/payback computed.
        @return pd.DataFrame
        """
        rows = []
        for p in (self.raw.projects or []):
            parts = p.get("participating_departments") or []
            dep_ids = self._extract_dep_ids(parts)

            timeline   = p.get("timeline", {}) or {}
            financials = p.get("financials", {}) or {}
            metrics    = p.get("metrics", {}) or {}

            start = self._to_dt(timeline.get("start_date"))
            end   = self._to_dt(timeline.get("end_date"))
            dur   = self._safe_int(timeline.get("duration_days"))
            if dur is None and (start is not None) and (end is not None):
                dur = int((end - start).days)

            budget      = self._to_float(financials.get("budget"))
            actual_cost = self._to_float(financials.get("actual_cost"))
            profit      = self._to_float(financials.get("profit"))
            roi_pct     = self._to_float(financials.get("roi_percentage"))

            rows.append({
                "project_id": p.get("project_id"),
                "name": p.get("name"),
                "status": p.get("status"),
                "duration_days": dur,
                "budget": budget,
                "actual_cost": actual_cost,
                "profit": profit,
                "roi_pct_explicit": roi_pct,
                "is_research": bool(dep_ids & RESEARCH_DEPS),
                "is_commercial": bool(dep_ids & COMMERCIAL_DEPS),
            })

        df = pd.DataFrame(rows)

        if df.empty:
            return df

        # Numerics
        for col in ["budget","actual_cost","profit","duration_days","roi_pct_explicit"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # ROI per project: roi_pct - profit/actual - profit/budget
        df["roi_ratio"] = np.nan
        has_explicit = df["roi_pct_explicit"].notna()
        mask_actual  = (~has_explicit) & df["actual_cost"].notna() & (df["actual_cost"] > 0) & df["profit"].notna()
        mask_budget  = (~has_explicit) & (~mask_actual) & df["budget"].notna() & (df["budget"] > 0) & df["profit"].notna()

        df.loc[has_explicit, "roi_ratio"] = df.loc[has_explicit, "roi_pct_explicit"] / 100.0
        df.loc[mask_actual,  "roi_ratio"] = df.loc[mask_actual,  "profit"] / df.loc[mask_actual,  "actual_cost"]
        df.loc[mask_budget,  "roi_ratio"] = df.loc[mask_budget,  "profit"] / df.loc[mask_budget,  "budget"]
        df["roi_pct"] = df["roi_ratio"] * 100.0

        # Payback: budget / (profit/day) when daily profit is positive
        daily_profit = df["profit"] / df["duration_days"].replace(0, np.nan)
        can_payback = (df["budget"] > 0) & daily_profit.notna() & (daily_profit > 0)
        df["payback_days"] = np.where(can_payback, df["budget"] / daily_profit, np.nan)

        # Success flag (for summaries)
        df["is_completed"] = df["status"].astype(str).str.lower().eq("completed")

        return df

    def _cohort_summary(self, sub: pd.DataFrame) -> Dict[str, float]:
        """
        @brief Compute metrics: avg & aggregate ROI, median payback, success rate.
        @param sub projects DataFrame
        @return dict metrics
        """
        if sub.empty:
            return dict(projects=0, profit_sum=0.0, cost_sum=0.0,
                        avg_roi_ratio=np.nan, avg_roi_pct=np.nan,
                        overall_roi_ratio=np.nan, overall_roi_pct=np.nan,
                        median_payback_days=np.nan, success_rate_pct=np.nan)

        # Cost base: prefer actual_cost, else budget
        cost_base = np.where(sub["actual_cost"].notna(), sub["actual_cost"], sub["budget"]).astype(float)
        cost_sum = float(np.nan_to_num(cost_base, nan=0.0).sum())
        profit_sum = float(sub["profit"].fillna(0).sum())

        overall_ratio = float(profit_sum / cost_sum) if cost_sum > 0 else np.nan
        avg_ratio = float(sub["roi_ratio"].mean())
        median_payback = float(sub["payback_days"].median()) if sub["payback_days"].notna().any() else np.nan
        success_rate = float(sub["is_completed"].mean() * 100.0)

        return dict(projects=int(len(sub)),
                    profit_sum=profit_sum, cost_sum=cost_sum,
                    avg_roi_ratio=avg_ratio, avg_roi_pct=avg_ratio*100.0 if np.isfinite(avg_ratio) else np.nan,
                    overall_roi_ratio=overall_ratio, overall_roi_pct=overall_ratio*100.0 if np.isfinite(overall_ratio) else np.nan,
                    median_payback_days=median_payback, success_rate_pct=success_rate)

    @staticmethod
    def _extract_dep_ids(parts: Iterable[dict]) -> Set[int]:
        """
        @brief Extract integer department_id set.
        @param parts Iterable of dicts from JSON
        @return set of department ids
        """
        ids: Set[int] = set()
        for it in parts or []:
            if isinstance(it, dict) and "department_id" in it:
                try:
                    ids.add(int(it["department_id"]))
                except Exception:
                    continue
        return ids

    @staticmethod
    def _to_dt(v):
        """
        @brief Safe datetime parser; returns NaT/None on failure.
        """
        try:
            return pd.to_datetime(v, errors="coerce")
        except Exception:
            return None

    @staticmethod
    def _safe_int(v):
        """
        @brief Safe int cast; returns None if not possible.
        """
        try:
            return int(v) if v is not None else None
        except Exception:
            return None

    @staticmethod
    def _to_float(v):
        """
        @brief Safe float cast; returns None if not possible.
        """
        try:
            return float(v) if v is not None else None
        except Exception:
            return None

    @staticmethod
    def _ensure_dir(path: str) -> None:
        """
        @brief Ensure output directory exists.
        @param path Directory path to create if missing
        """
        if path:
            os.makedirs(path, exist_ok=True)
