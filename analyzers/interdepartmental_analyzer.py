"""
@file interdepartmental_analyzer.py
@brief Computes: collaboration rate (share of projects with >= 2 departments),
top-5 partners by co-participation frequency,
effectiveness of joint projects by ROI.
"""

from typing import Dict, Any, List, Tuple
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from analyzers.base_rnd_analyzer import BaseAnalyzer
from config.messages import HEAD_COLLAB, ReportMsg, LogMsg
from config.enums import Thresholds


class InterdepartmentalAnalyzer(BaseAnalyzer):
    """
    @class InterdepartmentalAnalyzer
    @brief “Interdepartmental interaction” and the effectiveness of joint projects by ROI
"""

    def execute_analysis(self) -> Dict[str, Any]:
        """
        @brief Run the interdepartmental collaboration pipeline.
        @return dict 
    """
        self.logger.info(LogMsg.ANALYSIS_START.format("Interdepartmental Collaboration"))

        prj = self.projects_df()
        if prj is None or prj.empty:
            empty = pd.DataFrame(columns=[
                "partner_department_id","partner_department_name",
                "joint_projects","joint_completed","overall_roi_ratio","overall_roi_pct"
            ])
            return {
                "title": HEAD_COLLAB,
                "collaboration_rate_percent": 0.0,
                "joint_overall_roi_ratio": 0.0,
                "top_partners": empty,
                "partners_by_roi": empty,
            }

        for col in ("participating_departments", "is_completed", "budget", "actual_cost",
                    "profit", "roi_pct", "duration_days"):
            if col not in prj.columns:
                prj[col] = np.nan

        # mark joint projects
        self.logger.info(LogMsg.METRIC_START.format("collaboration_rate_percent"))
        part_counts = prj["participating_departments"].apply(self._safe_participants_len)
        is_joint = part_counts >= int(Thresholds.JOINT_MIN_DEPTS)
        collab_rate = float(is_joint.mean() * 100.0) if len(prj) else 0.0
        self.logger.info(LogMsg.METRIC_DONE.format("collaboration_rate_percent", f"{collab_rate:.1f}%"))

        joint_df = prj.loc[is_joint].copy()
        if joint_df.empty:
            empty = pd.DataFrame(columns=[
                "partner_department_id","partner_department_name",
                "joint_projects","joint_completed","overall_roi_ratio","overall_roi_pct"
            ])
            return {
                "title": HEAD_COLLAB,
                "collaboration_rate_percent": round(collab_rate, 1),
                "joint_overall_roi_ratio": 0.0,
                "top_partners": empty,
                "partners_by_roi": empty,
            }

        #ROI per project
        joint_df["budget"] = pd.to_numeric(joint_df["budget"], errors="coerce")
        joint_df["actual_cost"] = pd.to_numeric(joint_df["actual_cost"], errors="coerce")
        joint_df["profit"] = pd.to_numeric(joint_df["profit"], errors="coerce")
        joint_df["roi_pct"] = pd.to_numeric(joint_df["roi_pct"], errors="coerce")

        joint_df["roi_ratio"] = np.nan
        has_explicit = joint_df["roi_pct"].notna()
        mask_actual = (~has_explicit) & joint_df["actual_cost"].notna() & (joint_df["actual_cost"] > 0) & joint_df["profit"].notna()
        mask_budget = (~has_explicit) & (~mask_actual) & joint_df["budget"].notna() & (joint_df["budget"] > 0) & joint_df["profit"].notna()

        joint_df.loc[has_explicit, "roi_ratio"] = joint_df.loc[has_explicit, "roi_pct"] / 100.0
        joint_df.loc[mask_actual,  "roi_ratio"] = joint_df.loc[mask_actual,  "profit"] / joint_df.loc[mask_actual,  "actual_cost"]
        joint_df.loc[mask_budget,  "roi_ratio"] = joint_df.loc[mask_budget,  "profit"] / joint_df.loc[mask_budget,  "budget"]
        joint_df["roi_pct"] = joint_df["roi_ratio"] * 100.0

        #Overall ROI for all joint projects (aggregate)
        cost_base = np.where(joint_df["actual_cost"].notna(), joint_df["actual_cost"], joint_df["budget"])
        cost_sum = float(pd.Series(cost_base, index=joint_df.index).astype(float).fillna(0).sum())
        profit_sum = float(joint_df["profit"].fillna(0).sum())
        joint_overall_roi = float(profit_sum / cost_sum) if cost_sum > 0 else 0.0
        dep_name_map = self._department_name_map()
        partners_rows: List[Tuple[int, str, int, int]] = []

        for _, proj in joint_df.iterrows():
            parts = self._safe_participants_ids(proj.get("participating_departments"))
            for pid in parts:
                if pid == self.department_id:
                    continue
                partners_rows.append((
                    pid,
                    dep_name_map.get(pid, f"Department {pid}"),
                    1,
                    int(bool(proj.get("is_completed")))
                ))

        partners_df = pd.DataFrame(partners_rows, columns=[
            "partner_department_id","partner_department_name","joint_projects","joint_completed"
        ])

        if partners_df.empty:
            empty = pd.DataFrame(columns=[
                "partner_department_id","partner_department_name",
                "joint_projects","joint_completed","overall_roi_ratio","overall_roi_pct"
            ])
            return {
                "title": HEAD_COLLAB,
                "collaboration_rate_percent": round(collab_rate, 1),
                "joint_overall_roi_ratio": round(joint_overall_roi, 4),
                "top_partners": empty,
                "partners_by_roi": empty,
            }

        agg_freq = (partners_df
                    .groupby(["partner_department_id","partner_department_name"], as_index=False)
                    .agg({"joint_projects":"sum","joint_completed":"sum"}))

        # For ROI by partner, take all projects where this partner was together with other department
        rows_roi = []
        for pid, row in agg_freq.set_index("partner_department_id").iterrows():
            mask = joint_df["participating_departments"].apply(
                lambda L: self.department_id in self._safe_participants_ids(L) and pid in self._safe_participants_ids(L)
            )
            sub = joint_df.loc[mask].copy()
            if sub.empty:
                overall = np.nan
            else:
                base = np.where(sub["actual_cost"].notna(), sub["actual_cost"], sub["budget"])
                base_sum = float(pd.Series(base, index=sub.index).astype(float).fillna(0).sum())
                prof_sum = float(sub["profit"].fillna(0).sum())
                overall = float(prof_sum / base_sum) if base_sum > 0 else np.nan
            rows_roi.append({"partner_department_id": pid, "overall_roi_ratio": overall})

        roi_df = pd.DataFrame(rows_roi)
        partners_full = agg_freq.merge(roi_df, on="partner_department_id", how="left")
        partners_full["overall_roi_pct"] = partners_full["overall_roi_ratio"] * 100.0

        #TOP-5 by frequency
        top_partners = (partners_full
                        .sort_values(["joint_projects","overall_roi_ratio"], ascending=[False, False])
                        .head(5)
                        .reset_index(drop=True))

        #TOP-5 by ROI
        partners_by_roi = (partners_full
                           .sort_values("overall_roi_ratio", ascending=False, na_position="last")
                           .head(5)
                           .reset_index(drop=True))

        result = {
            "title": HEAD_COLLAB,
            "collaboration_rate_percent": round(collab_rate, 1),
            "joint_overall_roi_ratio": round(joint_overall_roi, 4),
            "top_partners": top_partners,
            "partners_by_roi": partners_by_roi,
        }

        self.logger.info(LogMsg.ANALYSIS_COMPLETE.format("Interdepartmental Collaboration"))
        return result

    def print(self, result: Dict[str, Any]) -> str:
        """
        @brief Convert analysis result to a readable section.
        """
        lines: List[str] = []
        lines.append(ReportMsg.COLLAB_RATE.format(result["collaboration_rate_percent"]))
        lines.append(f"Overall ROI of joint projects: {result['joint_overall_roi_ratio']:.3f}")

        #TOP-5 by frequency
        lines.append(ReportMsg.TOP_PARTNERS)
        tp = result.get("top_partners")
        if isinstance(tp, pd.DataFrame) and not tp.empty:
            for _, r in tp.iterrows():
                lines.append(
                    f"  • [{int(r['partner_department_id'])}] {r['partner_department_name']}: "
                    f"{int(r['joint_projects'])} projects, "
                    f"completed={int(r['joint_completed'])}, "
                    f"ROI={r['overall_roi_ratio']:.3f} ({r['overall_roi_pct']:.1f}%)"
                )
        else:
            lines.append(" no partners ")

        #TOP-5 by ROI
        roi_tbl = result.get("partners_by_roi")
        if isinstance(roi_tbl, pd.DataFrame) and not roi_tbl.empty:
            lines.append("\nTop partners by aggregate ROI:")
            for _, r in roi_tbl.iterrows():
                lines.append(
                    f"  • [{int(r['partner_department_id'])}] {r['partner_department_name']}: "
                    f"ROI={r['overall_roi_ratio']:.3f} ({r['overall_roi_pct']:.1f}%), "
                    f"projects={int(r['joint_projects'])}"
                )

        return "\n".join(lines)

    #Plots
    def plot_collab_rate_pie(self, out_dir: str = "plots") -> str:
        """
        @brief Save a pie chart: share of solo vs joint projects for the department.
        @param out_dir Output directory to save PNG
        @return str path to saved image
        """
        self._ensure_dir(out_dir)
        df = self.projects_df()
        part_counts = df["participating_departments"].apply(self._safe_participants_len)
        solo = int((part_counts < int(Thresholds.JOINT_MIN_DEPTS)).sum())
        joint = int((part_counts >= int(Thresholds.JOINT_MIN_DEPTS)).sum())

        plt.figure()
        plt.pie([solo, joint], labels=["Solo", "Joint"], autopct="%1.1f%%", startangle=90)
        plt.title("Collaboration rate (solo vs joint)")
        path = os.path.join(out_dir, "collaboration_rate_pie.png")
        plt.savefig(path, dpi=130, bbox_inches="tight")
        plt.close()
        return path

    def plot_top_partners_bar(self, result: Dict[str, Any], out_dir: str = "plots") -> str:
        """
        @brief Save a bar chart for top-5 partners by frequency.
        @param result Dict returned from execute_analysis()
        @param out_dir Output directory
        @return str path to saved image
        """
        self._ensure_dir(out_dir)
        tp = result.get("top_partners")
        if not isinstance(tp, pd.DataFrame) or tp.empty:
            return os.path.join(out_dir, "top_partners_bar.png")

        plt.figure()
        x = tp["partner_department_name"]
        y = tp["joint_projects"]
        plt.bar(x, y)
        plt.xticks(rotation=30, ha="right")
        plt.ylabel("Joint projects")
        plt.title("Top-5 partners by frequency")
        path = os.path.join(out_dir, "top_partners_bar.png")
        plt.tight_layout()
        plt.savefig(path, dpi=130)
        plt.close()
        return path

    def plot_partners_roi_bar(self, result: Dict[str, Any], out_dir: str = "plots") -> str:
        """
        @brief Save a bar chart for top-5 partners ranked by aggregate ROI.
        @param result Dict returned from execute_analysis()
        @param out_dir Output directory
        @return str path to saved image
        """
        self._ensure_dir(out_dir)
        tbl = result.get("partners_by_roi")
        if not isinstance(tbl, pd.DataFrame) or tbl.empty:
            return os.path.join(out_dir, "partners_by_roi_bar.png")

        plt.figure()
        x = tbl["partner_department_name"]
        y = tbl["overall_roi_ratio"]
        plt.bar(x, y)
        plt.xticks(rotation=30, ha="right")
        plt.ylabel("Aggregate ROI (ratio)")
        plt.title("Top-5 partners by ROI")
        path = os.path.join(out_dir, "partners_by_roi_bar.png")
        plt.tight_layout()
        plt.savefig(path, dpi=130)
        plt.close()
        return path

    def plot_joint_projects_roi_hist(self, out_dir: str = "plots", bins: int = 10) -> str:
        """
        @brief Save histogram of ROI for all joint projects of the department.
        @param out_dir Output directory
        @param bins    Number of histogram bins
        @return str path to saved image
        """
        self._ensure_dir(out_dir)
        prj = self.projects_df().copy()
        part_counts = prj["participating_departments"].apply(self._safe_participants_len)
        is_joint = part_counts >= int(Thresholds.JOINT_MIN_DEPTS)
        df = prj.loc[is_joint].copy()

        # compute roi like in execute_analysis
        df["budget"] = pd.to_numeric(df.get("budget"), errors="coerce")
        df["actual_cost"] = pd.to_numeric(df.get("actual_cost"), errors="coerce")
        df["profit"] = pd.to_numeric(df.get("profit"), errors="coerce")
        df["roi_pct"] = pd.to_numeric(df.get("roi_pct"), errors="coerce")
        roi = np.nan * np.ones(len(df))
        has_explicit = df["roi_pct"].notna()
        roi[has_explicit.values] = (df.loc[has_explicit, "roi_pct"] / 100.0).values
        m_act = (~has_explicit) & df["actual_cost"].notna() & (df["actual_cost"] > 0) & df["profit"].notna()
        roi[m_act.values] = (df.loc[m_act, "profit"] / df.loc[m_act, "actual_cost"]).values
        m_bud = (~has_explicit) & (~m_act) & df["budget"].notna() & (df["budget"] > 0) & df["profit"].notna()
        roi[m_bud.values] = (df.loc[m_bud, "profit"] / df.loc[m_bud, "budget"]).values
        roi = pd.to_numeric(pd.Series(roi), errors="coerce").dropna()

        plt.figure()
        plt.hist(roi, bins=bins)
        plt.xlabel("ROI (ratio)")
        plt.ylabel("Projects")
        plt.title("Joint projects - ROI distribution")
        path = os.path.join(out_dir, "joint_projects_roi_hist.png")
        plt.tight_layout()
        plt.savefig(path, dpi=130)
        plt.close()
        return path


    @staticmethod
    def _safe_participants_len(value) -> int:
        """
        @brief Safe length getter for participating_departments.
        @param value Raw field from JSON
        @return int length
        """
        return len(value) if isinstance(value, list) else 0

    @staticmethod
    def _safe_participants_ids(value) -> List[int]:
        """
        @brief Extract list of department_id.
        @param value Raw field 
        @return list of ints
        """
        if not isinstance(value, list):
            return []
        ids: List[int] = []
        for it in value:
            if isinstance(it, dict) and "department_id" in it:
                try:
                    ids.append(int(it["department_id"]))
                except Exception:
                    continue
        return ids

    def _department_name_map(self) -> Dict[int, str]:
        """
        @brief Build mapping department_id.
        """
        mapping: Dict[int, str] = {}
        try:
            for d in (self.raw.departments or []):
                did = d.get("id")
                name = d.get("name")
                if did is not None and name:
                    mapping[int(did)] = str(name)
        except Exception:
            pass
        mapping.setdefault(self.department_id, f"Department {self.department_id}")
        return mapping

    @staticmethod
    def _ensure_dir(path: str) -> None:
        """
        @brief Ensure that output directory exists.
        @param path Directory path
        """
        if path:
            os.makedirs(path, exist_ok=True)
