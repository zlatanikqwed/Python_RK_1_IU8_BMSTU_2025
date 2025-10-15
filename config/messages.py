"""
@brief Centralized user-facing strings and section headers.
       Contains banners, section titles, logging templates and short report phrases
       for R&D analyses.
"""
HEAD_SCIENCE   = "1) SCIENTIFIC POTENTIAL"
HEAD_PROJECTS  = "2) PROJECT ANALYSIS"
HEAD_INNOVATION= "3) INNOVATION EFFECTIVENESS"
HEAD_COLLAB    = "4) INTERDEPARTMENTAL COLLABORATION"
HEAD_STRATEGY  = "5) DEVELOPMENT STRATEGY"

class LogMsg:
    """
    @brief Standardized log templates to be used across analyzers.
    """

    # System lifecycle
    SYSTEM_START   = "R&D Analysis system initialization started"
    SYSTEM_READY   = "R&D Analysis system ready"
    DATA_LOAD_START     = "Starting data loading from JSON"
    DATA_LOAD_OK        = "Data successfully loaded from file: {}"
    DATA_LOAD_FAIL      = "Failed to load JSON: {} - {}"

    # Processing
    ANALYSIS_START = "Starting {} analysis"
    ANALYSIS_COMPLETE = "{} analysis completed successfully"
    ANALYSIS_ERROR = "Error during {} analysis: {}"

    # Data processing messages
    DATA_PROCESSING_START = "Starting data processing for {}"
    DATA_FILTERING_START = "Filtering IT equipment from dataset"
    DATA_TRANSFORMATION_START = "Starting data transformation"
    
    # Metrics
    COUNT_ITEMS    = "Items in scope: {}"
    METRIC_START   = "Calculating metric: {}"
    METRIC_DONE    = "Metric calculated: {} = {}"



class ReportMsg:
    """
    @class ReportMsg
    @brief Readable one-liners for report output.
    """

    # Section headers

    DEGREE_HEADER      = "Degree distribution (canonical)"
    AVG_CERTS          = "Average certificates per employee: {:.2f}"
    TOP_PERFORMERS     = "Employees with degree & performance_score > 85: {}"

    AVG_DURATION       = "Average project duration (days): {:.1f}"
    SUCCESS_RATE       = "Project success rate (completed/total): {:.1f}%"
    LONGEST_PROJECT    = "Longest project (days): {}"

    ROI_RND            = "Average ROI - R&D: {:.2f}"
    ROI_COMM           = "Average ROI - Commercial: {:.2f}"
    PAYBACK_MEDIAN     = "Typical payback (median, days): {}"

    COLLAB_RATE        = "Collaboration rate (joint projects): {:.1f}%"
    JOINT_SUCCESS      = "Success rate for joint projects: {:.1f}%"
    TOP_PARTNERS       = "Top partners (by frequency)"

    OPT_BUDGET         = "Optimal annual R&D budget (estimate): {:,.0f} RUB"
    SUCCESS_CRITERIA   = "Success criteria (checklist)"
    METRICS_SET        = "Monitoring metrics (KPI set)"


class ErrMsg:
    """
    @class ErrMsg
    @brief Standardized error messages for exceptions and validation.
    """
    FILE_NOT_FOUND   = "File not found: {}"
    INVALID_JSON     = "Invalid JSON format in {}"
    DATA_EMPTY       = "Expected data is empty: {}"
    CALC_ERROR       = "Calculation error in {}: {}"
    VALIDATION_FAIL  = "Validation failed: {}"
