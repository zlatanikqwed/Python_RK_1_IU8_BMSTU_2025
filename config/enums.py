"""
@brief Enumerations and canonical maps used across analyzers.
       Includes IT infrastructure enums and R&D enums 
       to simplify imports and keep types consistent.
"""

from enum import Enum

class Degree(Enum):
    """
    @brief Canonical scientific degree classes for normalization.
    """
    DSC      = "dsc"       # Doctor of Science
    PHD      = "phd"       # Candidate of Sciences
    MASTER   = "master"    # Master's degree
    BACHELOR = "bachelor"  # Bachelor
    NONE     = "none"      # No degree
    OTHER    = "other"     # All other

DEGREE_ORDER = [d.value for d in (Degree.DSC, Degree.PHD, Degree.MASTER,
                                  Degree.BACHELOR, Degree.NONE, Degree.OTHER)]

class ProjectType(Enum):
    """
    @brief Project portfolio classification for ROI comparison.
    """
    RESEARCH        = "Research"
    COMMERCIAL      = "Commercial"


class ProjectStatus(Enum):
    """
    @brief Canonical project statuses.
    """
    PLANNED   = "planned"
    ACTIVE    = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RiskLevel(Enum):
    """
    @brief Risk category used in portfolio views.
    """
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


class Priority(Enum):
    """
    @brief Priority of project execution.
    """
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"

class Thresholds:
    """
    @class Thresholds
    @brief Numeric thresholds used across analyzers.
    """
    # Scientific potential
    PERF_TOP: float = 85.0     # @brief performance_score > 85 - top performer

    # Collaboration
    JOINT_MIN_DEPTS: int = 2   # @brief joint project if ≥ 2 departments

# @brief Degree normalization map for Russian labels.
DEGREE_MAP_RU = {
    # Doctoral
    "доктор наук": Degree.DSC.value,
    # PhD
    "кандидат наук": Degree.PHD.value,
    # Master
    "магистратура": Degree.MASTER.value,
    # Higher
    "высшее": Degree.BACHELOR.value,
    # Secondary / None
    "среднее специальное": Degree.NONE.value,
}