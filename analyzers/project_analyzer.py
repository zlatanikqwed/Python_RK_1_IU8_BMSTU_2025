"""
@file project_analyzer.py
@brief Uses normalized projects DataFrame prepared by BaseAnalyzer to compute:
        average project duration (days),
        success rate (completed/total),
        the longest project (by duration_days).
"""

from typing import Dict, Any, List
import os
import pandas as pd
import matplotlib.pyplot as plt

from analyzers.base_rnd_analyzer import BaseAnalyzer
from config.messages import HEAD_PROJECTS, ReportMsg, LogMsg
from config.enums import ProjectStatus


class ProjectAnalyzer(BaseAnalyzer):
    """
    @class ProjectAnalyzer
    @brief Computes metrics for projects.
    """

    def execute_analysis(self) -> Dict[str, Any]:
        """
        @brief Run project analysis pipeline.
        @return dict
        """
        self.logger.info(LogMsg.ANALYSIS_START.format("Project Analysis"))

        df = self.projects_df()
        if df is None or df.empty:
            self.logger.info("Projects DataFrame is empty - returning zeros")
            return {
                "title": HEAD_PROJECTS,
                "avg_duration_days": 0.0,
                "success_rate_percent": 0.0,
                "longest_project": pd.DataFrame(
                    columns=["project_id", "name", "duration_days", "status", "start_date", "end_date"]
                )
            }

        for col in ("duration_days", "status", "start_date", "end_date"):
            if col not in df.columns:
                df[col] = None

        # Average duration (days)
        self.logger.info(LogMsg.METRIC_START.format("avg_duration_days"))
        dur = pd.to_numeric(df["duration_days"], errors="coerce")
        avg_duration = float(dur.mean()) if len(df) else 0.0
        self.logger.info(LogMsg.METRIC_DONE.format("avg_duration_days", round(avg_duration, 1)))

        # Success rate (completed/total)
        self.logger.info(LogMsg.METRIC_START.format("success_rate_percent"))
        status = df["status"].astype(str).str.lower()
        completed_mask = status.eq(ProjectStatus.COMPLETED.value)
        success_rate = float((completed_mask.mean() * 100.0) if len(df) else 0.0)
        self.logger.info(LogMsg.METRIC_DONE.format("success_rate_percent", round(success_rate, 1)))

        # Longest project (by duration_days)
        self.logger.info(LogMsg.METRIC_START.format("longest_project"))
        longest = (
            df.assign(duration_days=pd.to_numeric(df["duration_days"], errors="coerce"))
              .sort_values("duration_days", ascending=False)
              .loc[:, ["project_id", "name", "duration_days", "status", "start_date", "end_date"]]
              .head(1)
        )
        self.logger.info(
            LogMsg.METRIC_DONE.format(
                "longest_project",
                int(longest["duration_days"].iloc[0]) if not longest.empty else 0
            )
        )

        result = {
            "title": HEAD_PROJECTS,
            "avg_duration_days": round(avg_duration, 1),
            "success_rate_percent": round(success_rate, 1),
            "longest_project": longest.reset_index(drop=True)
        }
        self.logger.info(LogMsg.ANALYSIS_COMPLETE.format("Project Analysis"))
        return result

    def print(self, result: Dict[str, Any]) -> str:
        """
        @brief Convert analysis result dict to a readable string.
        @param result Output of execute_analysis()
        @return str formatted section for console
        """
        lines: List[str] = []

        lines.append(ReportMsg.AVG_DURATION.format(result["avg_duration_days"]))
        lines.append(ReportMsg.SUCCESS_RATE.format(result["success_rate_percent"]))

        lp = result.get("longest_project")
        if isinstance(lp, pd.DataFrame) and not lp.empty:
            r = lp.iloc[0]
            lines.append(f"Longest project: [{r['project_id']}] {r['name']} - {int(r['duration_days'])} days")
        else:
            lines.append("Longest project: - ")
        return "\n".join(lines)

    # Plots

    def plot_duration_hist(self, result: Dict[str, Any], bins: int = 10, out_dir: str = "plots") -> str:
        """
        @brief Save a histogram of project durations (days).
        @param result Dict returned by execute_analysis() 
        @param bins Number of histogram bins
        @param out_dir Output directory to save file
        @return str path to PNG file
        """
        self._ensure_dir(out_dir)
        df = self.projects_df()
        durations = pd.to_numeric(df["duration_days"], errors="coerce").dropna()

        plt.figure()
        plt.hist(durations, bins=bins)
        plt.xlabel("Duration, days")
        plt.ylabel("Projects")
        plt.title("Projects - Duration distribution")
        path = os.path.join(out_dir, "projects_duration_hist.png")
        plt.tight_layout()
        plt.savefig(path, dpi=130)
        plt.close()
        return path

    def plot_status_pie(self, result: Dict[str, Any], out_dir: str = "plots") -> str:
        """
        @brief Save a pie chart of project statuses (completed / other statuses).
        @param result Dict from execute_analysis()
        @param out_dir Output directory
        @return str path to PNG file
        """
        self._ensure_dir(out_dir)
        df = self.projects_df()
        status_counts = (
            df["status"].astype(str).str.lower().replace("", "unknown").value_counts().sort_index()
        )

        plt.figure()
        plt.pie(status_counts.values, labels=status_counts.index, autopct="%1.0f%%", startangle=90)
        plt.title("Projects - Status breakdown")
        path = os.path.join(out_dir, "projects_status_pie.png")
        plt.tight_layout()
        plt.savefig(path, dpi=130)
        plt.close()
        return path

    def plot_top_longest(self, result: Dict[str, Any], k: int = 10, out_dir: str = "plots") -> str:
        """
        @brief Save a bar chart for the top longest projects.
        @param result Dict from execute_analysis()
        @param Number of projects to show
        @param out_dir Output directory
        @return str path to PNG file
        """
        self._ensure_dir(out_dir)
        df = self.projects_df().assign(
            duration_days=pd.to_numeric(self.projects_df()["duration_days"], errors="coerce")
        )
        top = (
            df.dropna(subset=["duration_days"])
              .sort_values("duration_days", ascending=False)
              .head(k)[["name", "duration_days"]]
        )

        plt.figure()
        plt.barh(top["name"][::-1], top["duration_days"][::-1])
        plt.xlabel("Duration, days")
        plt.title(f"Top {len(top)} longest projects")
        plt.tight_layout()
        path = os.path.join(out_dir, "projects_top_longest.png")
        plt.savefig(path, dpi=130)
        plt.close()
        return path


    @staticmethod
    def _ensure_dir(path: str) -> None:
        """
        @brief Output directory exists.
        @param path Directory path to create if missing
        """
        if path:
            os.makedirs(path, exist_ok=True)
