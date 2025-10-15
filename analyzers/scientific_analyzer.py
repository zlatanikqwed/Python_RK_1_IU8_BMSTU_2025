"""
@file scientific_analyzer.py
@brief Consumes normalized employees DataFrame from BaseAnalyzer and computes:
        degree distribution (canonical order),
        average certificates per employee,
        top performers: employees with a scientific degree and performance_score > threshold.
"""

from typing import Dict, Any, List
import os
import pandas as pd
import matplotlib.pyplot as plt

from analyzers.base_rnd_analyzer import BaseAnalyzer
from config.messages import HEAD_SCIENCE, ReportMsg, LogMsg
from config.enums import DEGREE_ORDER, Thresholds


class ScientificAnalyzer(BaseAnalyzer):
    """
    @class ScientificAnalyzer
    @brief Computes metrics on top.
    """

    def execute_analysis(self) -> Dict[str, Any]:
        """
        @brief Run the scientific potential analysis pipeline.
        @return dict 
        """
        self.logger.info(LogMsg.ANALYSIS_START.format("Scientific Potential"))

        df = self.employees_df()
        if df is None or df.empty:
            self.logger.info("Employees DataFrame is empty - returning zeros")
            result = {
                "degree_distribution": pd.Series(index=DEGREE_ORDER, dtype=int).fillna(0).astype(int),
                "avg_certificates_per_employee": 0.0,
                "top_performers": pd.DataFrame(
                    columns=["employee_id", "full_name", "position", "degree", "performance_score", "certifications"]
                )
            }
            self.logger.info(LogMsg.ANALYSIS_COMPLETE.format("Scientific Potential"))
            return result

        for col in ("degree", "certifications", "performance_score"):
            if col not in df.columns:
                df[col] = None

        # Degree distribution in canonical order
        self.logger.info(LogMsg.METRIC_START.format("degree_distribution"))
        dist = df["degree"].value_counts(dropna=False).reindex(DEGREE_ORDER, fill_value=0).astype(int)
        self.logger.info(LogMsg.METRIC_DONE.format("degree_distribution", int(dist.sum())))

        # Average certificates per employee
        self.logger.info(LogMsg.METRIC_START.format("avg_certificates_per_employee"))
        avg_certs = float(pd.to_numeric(df["certifications"], errors="coerce").fillna(0).mean())
        self.logger.info(LogMsg.METRIC_DONE.format("avg_certificates_per_employee", round(avg_certs, 2)))

        # Top performers: degree = dsc/phd and performance_score > threshold
        self.logger.info(LogMsg.METRIC_START.format("top_performers"))
        perf_thr = Thresholds.PERF_TOP
        valid_science = {"phd", "dsc"}
        mask_has_degree = df["degree"].astype(str).str.lower().isin(valid_science)
        mask_perf = pd.to_numeric(df["performance_score"], errors="coerce") > perf_thr
        top = (
            df.loc[mask_has_degree & mask_perf, ["employee_id", "full_name", "position",
                                                 "degree", "performance_score", "certifications"]]
              .sort_values(["performance_score", "degree"], ascending=[False, True])
              .reset_index(drop=True)
        )
        self.logger.info(LogMsg.METRIC_DONE.format("top_performers", len(top)))

        result = {
            "degree_distribution": dist,
            "avg_certificates_per_employee": round(avg_certs, 2),
            "top_performers": top
        }
        self.logger.info(LogMsg.ANALYSIS_COMPLETE.format("Scientific Potential"))
        return result

    def print(self, result: Dict[str, Any]) -> str:
        """
        @brief Convert analysis result dict to a readable multiline string.
        @param result Output of execute_analysis()
        @return str formatted section ready for console
        """
        lines: List[str] = []

        # Degree distribution
        lines.append(ReportMsg.DEGREE_HEADER + ":")
        dist = result["degree_distribution"]
        if isinstance(dist, pd.Series) and not dist.empty:
            for deg in dist.index:
                lines.append(f"  - {deg}: {int(dist.loc[deg])}")
        else:
            lines.append("  - no data")

        # Average certificates
        lines.append(ReportMsg.AVG_CERTS.format(result["avg_certificates_per_employee"]))

        # Top performers
        tp = result["top_performers"]
        if isinstance(tp, pd.DataFrame) and not tp.empty:
            lines.append(ReportMsg.TOP_PERFORMERS.format(len(tp)))
            head = tp.head(10).copy()
            for _, r in head.iterrows():
                lines.append(
                    f"    * [{r['employee_id']}] {r['full_name']} - {r['position']}; "
                    f"degree={r['degree']}; score={r['performance_score']}; certs={r['certifications']}"
                )
            if len(tp) > 10:
                lines.append(f"    ... and {len(tp) - 10} more")
        else:
            lines.append(ReportMsg.TOP_PERFORMERS.format(0))

        return "\n".join(lines)

    #Plotting API 
    def _ensure_outdir(self, out_dir: str) -> str:
        """
        @brief Ensure output folder exists.
        @param out_dir where plots will be saved
        @return str normalized output path
        @throws OSError if folder cannot be created
        """
        os.makedirs(out_dir, exist_ok=True)
        return out_dir

    def plot_degree_distribution(self, result: Dict[str, Any], out_dir: str = "plots") -> str:
        """
        @brief Save bar plot of degree distribution (canonical order).
        @param result Dict returned by execute_analysis()
        @param out_dir Folder to save the plot into
        @return str path to saved PNG
        """
        self._ensure_outdir(out_dir)
        series = result.get("degree_distribution")
        path = os.path.join(out_dir, "degree_distribution.png")

        if not isinstance(series, pd.Series) or series.empty:
            fig = plt.figure()
            plt.title("Degree distribution (no data)")
            plt.savefig(path, bbox_inches="tight")
            plt.close(fig)
            return path

        fig = plt.figure()
        series.loc[DEGREE_ORDER].astype(int).plot(kind="bar")
        plt.title("Degree distribution")
        plt.xlabel("degree")
        plt.ylabel("count")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path
    
    def plot_degree_pie(self, result: Dict[str, Any], out_dir: str = "plots") -> str:
        """
        @brief Save pie chart showing degree distribution across employees.
        @param result Dict returned by execute_analysis()
        @param out_dir Folder to save the plot into
        @return str path to saved PNG
        @note Uses canonical degree order for visual consistency.
        """

        # ensure directory
        self._ensure_outdir(out_dir)
        path = os.path.join(out_dir, "degree_distribution_pie.png")

        # fetch data
        series = result.get("degree_distribution")
        if not isinstance(series, pd.Series) or series.empty:
            fig = plt.figure()
            plt.title("Degree distribution (no data)")
            plt.savefig(path, bbox_inches="tight")
            plt.close(fig)
            return path

        series = series.reindex(DEGREE_ORDER, fill_value=0)
        data = series[series > 0]

        fig, ax = plt.subplots(figsize=(6, 6))
        wedges, texts, autotexts = ax.pie(
            data.values,
            labels=data.index,
            autopct="%1.1f%%",
            startangle=90,
            counterclock=False
        )
        ax.axis("equal")  # equal aspect ratio ensures circular pie
        plt.title("Degree distribution (canonical order)")
        plt.tight_layout()
        plt.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path

    def plot_certificates_pie(self, out_dir: str = "plots") -> str:
        """
        @brief Save pie chart of certificate count distribution per employee.
        @param out_dir Folder to save the plot into
        @return str path to saved PNG
        @note Certificates are grouped into bins.
        """

        self._ensure_outdir(out_dir)
        path = os.path.join(out_dir, "certificates_pie.png")

        df = self.employees_df()
        if df is None or df.empty or "certifications" not in df.columns:
            fig = plt.figure()
            plt.title("Certificates distribution (no data)")
            plt.savefig(path, bbox_inches="tight")
            plt.close(fig)
            return path

        vals = pd.to_numeric(df["certifications"], errors="coerce").fillna(0)
        bins = {
            "0": (vals == 0).sum(),
            "1–2": ((vals >= 1) & (vals <= 2)).sum(),
            "3–4": ((vals >= 3) & (vals <= 4)).sum(),
            "5+": (vals >= 5).sum(),
        }

        data = {k: v for k, v in bins.items() if v > 0}

        fig, ax = plt.subplots(figsize=(6, 6))
        wedges, texts, autotexts = ax.pie(
            data.values(),
            labels=data.keys(),
            autopct="%1.1f%%",
            startangle=90,
            counterclock=False
        )
        ax.axis("equal")
        plt.title("Certificates per employee (grouped)")
        plt.tight_layout()
        plt.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path
