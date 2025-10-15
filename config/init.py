"""
@file __init__.py
@brief For Task 5 configuration: messages & enums.
       Centralizes constants, headers and canonical types.
"""

# Messages (banners, headings, report phrases, error strings)
from .messages import (
    HEAD_SCIENCE, HEAD_PROJECTS, HEAD_INNOVATION, HEAD_COLLAB, HEAD_STRATEGY,
    LogMsg, ReportMsg, ErrMsg,
)

# Enums, thresholds and normalization maps
from .enums import (
    Degree, DEGREE_ORDER, DEGREE_MAP_RU,
    ProjectStatus, ProjectType,
    RiskLevel, Priority,
    Thresholds,
)

__all__ = [
    # messages
    "HEAD_SCIENCE", "HEAD_PROJECTS", "HEAD_INNOVATION", "HEAD_COLLAB", "HEAD_STRATEGY",
    "LogMsg", "ReportMsg", "ErrMsg",
    # enums & constants,
    "Degree", "DEGREE_ORDER", "DEGREE_MAP_RU",
    "ProjectStatus", "ProjectType",
    "RiskLevel", "Priority",
    "Thresholds",
]
