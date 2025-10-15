"""
@file main.py
@brief Entry point for full report (R&D dept). Orchestrates all 5 analyzers:
       1) Scientific potential
       2) Project analysis
       3) Innovation effectiveness
       4) Interdepartmental collaboration
       5) Development strategy
"""

from __future__ import annotations
import argparse
import os

from analyzers.scientific_analyzer import ScientificAnalyzer
from analyzers.project_analyzer import ProjectAnalyzer
from analyzers.innovative_analyzer import InnovativeAnalyzer
from analyzers.interdepartmental_analyzer import InterdepartmentalAnalyzer
from analyzers.strategy_analyzer import StrategyAnalyzer

from config.messages import HEAD_SCIENCE, HEAD_PROJECTS, HEAD_INNOVATION, HEAD_COLLAB, HEAD_STRATEGY

from utilits.logger import analysis_logger

from utilits.report_pdf import PDFReport


def _print_section(title: str, body: str) -> None:
    """
    @brief Prints a titled section.
    @param title Section title
    @param body Pre-formatted string
    """
    print("\n" + title)
    print("-" * 70)
    print(body)


def _ensure_dir(path: str) -> None:
    """
    @brief Create directory if missing.
    """
    if path:
        os.makedirs(path, exist_ok=True)


def main() -> int:
    """
    @brief Orchestrate all analyzers and print the full report.
    @return Exit code (0 - success)
    """
    parser = argparse.ArgumentParser(description="Full R&D Report")
    parser.add_argument("json_path", help="Path to company.json")
    parser.add_argument("--department-id", type=int, default=26,
                        help="Target department id (default: 26)")
    parser.add_argument("--out-dir", default=None,
                        help="Output dir for CSV/MD exports (optional)")
    parser.add_argument("--export", action="store_true",
                        help="Export CSV/MD artifacts for grading")
    args = parser.parse_args()

    logger = analysis_logger.get_logger("Main")
    logger.info("Starting Task 5 report pipeline")


    # 1) Scientific Potential
    sci = ScientificAnalyzer(args.json_path, department_id=args.department_id)
    sci_res = sci.execute_analysis()
    _print_section(HEAD_SCIENCE, sci.print(sci_res))
    #plots
    deg_png = sci.plot_degree_distribution(sci_res, out_dir="plots")
    pie_png  = sci.plot_degree_pie(sci_res, out_dir="plots")
    cert_pie = sci.plot_certificates_pie(out_dir="plots")
    print("Saved:", deg_png, pie_png, cert_pie)

    # 2) Project Analysis
    proj = ProjectAnalyzer(args.json_path, department_id=args.department_id)
    proj_res = proj.execute_analysis()
    _print_section(HEAD_PROJECTS, proj.print(proj_res))
    #plots
    dur_hist = proj.plot_duration_hist(proj_res, bins=10, out_dir="plots")
    status_pie = proj.plot_status_pie(proj_res, out_dir="plots")
    top_long   = proj.plot_top_longest(proj_res, k=10, out_dir="plots")
    print("Saved:", dur_hist, status_pie, top_long)
    
    # 3) Innovation Effectiveness 
    innov = InnovativeAnalyzer(args.json_path, department_id=args.department_id)
    innov_res = innov.execute_analysis()
    _print_section(HEAD_INNOVATION, innov.print(innov_res))
    #plots
    inn_bars = innov.plot_cohort_roi_bars(innov_res, out_dir="plots")
    inn_hist = innov.plot_roi_hist_by_cohort(out_dir="plots", bins=10)
    inn_pay  = innov.plot_payback_hist_rnd(out_dir="plots", bins=10)
    inn_scat = innov.plot_roi_vs_duration_scatter(out_dir="plots")
    print("Saved:", inn_bars, inn_hist, inn_pay, inn_scat)

    # 4) Interdepartmental Collaboration
    collab = InterdepartmentalAnalyzer(args.json_path, department_id=args.department_id)
    collab_res = collab.execute_analysis()
    _print_section(HEAD_COLLAB, collab.print(collab_res))
    #plots
    c_pie = collab.plot_collab_rate_pie(out_dir="plots")
    c_top = collab.plot_top_partners_bar(collab_res, out_dir="plots")
    c_roi = collab.plot_partners_roi_bar(collab_res, out_dir="plots")
    c_hist = collab.plot_joint_projects_roi_hist(out_dir="plots", bins=10)
    print("Saved:", c_pie, c_top, c_roi, c_hist)

    # 5) Development Strategy 
    strat = StrategyAnalyzer(args.json_path, department_id=args.department_id)
    strat_res = strat.execute_analysis()
    _print_section(HEAD_STRATEGY, strat.print(strat_res))

    if args.export:
        os.makedirs("plots", exist_ok=True)

        #Path for image
        imgs = {
            "degree_pie":         os.path.join("plots", "degree_distribution_pie.png"),
            "degree":             os.path.join("plots", "degree_distribution.png"),
            "cert_pie":           os.path.join("plots", "certificates_pie.png"),
            "proj_dur":           os.path.join("plots", "projects_duration_hist.png"),
            "proj_pie":           os.path.join("plots", "projects_status_pie.png"),
            "proj_toplong":       os.path.join("plots", "projects_top_longest.png"),
            "innov_scatter":      os.path.join("plots", "innovation_rnd_payback_hist.png"),
            "innov_main":         os.path.join("plots", "innovation_roi_hist.png"),
            "innov_rnd_com":      os.path.join("plots", "innovation_cohort_roi_bars.png"),
            "innov_sct":          os.path.join("plots", "innovation_scatter_roi_duration.png"),
            "collab_pie":         os.path.join("plots", "collaboration_rate_pie.png"),
            "collab_top":         os.path.join("plots", "top_partners_bar.png"),
            "collab_roi":         os.path.join("plots", "partners_by_roi_bar.png"),
            "collab_roi_hist":    os.path.join("plots", "joint_projects_roi_hist.png"),
        }

        #Form text sections 
        sci_text    = sci.print(sci_res)
        proj_text   = proj.print(proj_res)
        innov_text  = innov.print(innov_res)
        collab_text = collab.print(collab_res)
        strat_text  = strat.print(strat_res)

        out_pdf = os.path.join(args.out_dir or ".", "R&D_Report.pdf")
        pdf = PDFReport(title="Company R&D Report")
        pdf.add_section(HEAD_SCIENCE, sci_text)
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 13)
        pdf.multi_cell(0, 7, "Scientific - charts")
        pdf.ln(4)
        pdf.image(imgs["degree_pie"], x=15, y=pdf.get_y(), w=85)
        pdf.image(imgs["degree"], x=110, y=pdf.get_y(), w=85)
        pdf.ln(90) 
        pdf.image(imgs["cert_pie"], x=15, y=pdf.get_y(), w=180)

        pdf.add_section(HEAD_PROJECTS, proj_text)
        pdf.add_image_grid("Projects - charts", [
            ("", imgs["proj_dur"]),
            ("", imgs["proj_pie"]),
            ("", imgs["proj_toplong"]),
        ])

        pdf.add_section(HEAD_INNOVATION, innov_text)
        pdf.add_image_grid("Innovation - charts", [
            ("", imgs["innov_scatter"]),
            ("", imgs["innov_main"]),
            ("", imgs["innov_rnd_com"]),
            ("", imgs["innov_sct"])
        ])

        pdf.add_section(HEAD_COLLAB, collab_text)
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 13)
        pdf.multi_cell(0, 7, "Collaboration - charts")
        pdf.ln(4)
        pdf.image(imgs["collab_pie"], x=15, y=pdf.get_y(), w=85)
        pdf.image(imgs["collab_top"], x=110, y=pdf.get_y(), w=85)
        pdf.ln(90) 
        pdf.image(imgs["collab_roi"], x=15, y=pdf.get_y(), w=85)
        pdf.image(imgs["collab_roi_hist"], x=110, y=pdf.get_y(), w=85)

        pdf.add_section(HEAD_STRATEGY, strat_text)
        out_dir = args.out_dir or "out"
        out_pdf = os.path.join(out_dir, "R&D_Report.pdf")
        os.makedirs(out_dir, exist_ok=True)
        pdf.output(out_pdf)
        print(f"PDF saved to: {out_pdf}")
        pdf.output(out_pdf)
        print("PDF report saved:", out_pdf)

    logger.info("Report pipeline finished successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
