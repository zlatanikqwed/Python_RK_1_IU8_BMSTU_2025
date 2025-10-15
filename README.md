# Python_RK_1_IU8_BMSTU_2025
Вариант 5. 
---
**Студент:**
Аналитик R&D

**Отдел:**
Исследовательский центр (ID: 26)

---

## Задание

Проведите анализ исследовательской деятельности:

### 1. Научный потенциал

- Проанализируйте распределение ученых степеней в отделе.  
- Определите среднее количество сертификатов на одного сотрудника.  
- Найдите сотрудников с ученой степенью и *performance_score* > 85.

### 2. Проектный анализ

- Рассчитайте среднюю длительность исследовательских проектов.  
- Определите *success rate* проектов (*completed/total*).  
- Найдите самый длительный исследовательский проект.

### 3. Инновационная эффективность

- Рассчитайте *ROI* по исследовательским проектам.  
- Сравните эффективность R&D проектов с коммерческими.  
- Определите время окупаемости типичного исследовательского проекта.

### 4. Межотделенное взаимодействие

- Проанализируйте *collaboration* отдела с другими подразделениями.  
- Найдите наиболее частых партнеров по проектам.  
- Оцените эффективность совместных проектов.

### 5. Стратегия развития

- Определите критерии для оценки успешности R&D проектов.  
- Рассчитайте оптимальный бюджет для исследовательской деятельности.  
- Разработайте систему метрик для мониторинга инновационной активности.

---

## Структура

```text
project/
├── analyzers/
│ ├── base_rnd_analyzer.py
│ ├── innovative_analyzer.py
│ ├── interdepartmental_analyzer.py
│ ├── project_analyzer.py
│ ├── scientific_analyzer.py
│ ├── strategy_analyzer.py
│ └── init.py
├── config/
│ ├── enums.py
│ ├── init.py
│ └── messages.py
├── logs/
├── out/
│ └── R&D_Report.pdf
├── plots/
├── utilits/
│ ├── fonts/
│ ├── init.py
│ ├── logger.py
│ └── report_pdf.py
├── company.json
├── main.py
```
---

## Технические зависимости

### Основные требования

```text
fpdf==1.7.2
matplotlib==3.10.7
numpy==2.3.4
pandas==2.3.3
```
---

## Результат работы программы

```text
2025-10-16 01:19:11 - Main - INFO - Starting Task 5 report pipeline
2025-10-16 01:19:11 - ScientificAnalyzer - INFO - Initializing BaseAnalyzer
2025-10-16 01:19:11 - ScientificAnalyzer - INFO - Starting JSON load
2025-10-16 01:19:12 - ScientificAnalyzer - INFO - JSON loaded: meta=True, dep=30, emp=755, proj=100, eq=200
2025-10-16 01:19:12 - ScientificAnalyzer - INFO - Employees DF built: 21 rows for department_id=26
2025-10-16 01:19:12 - ScientificAnalyzer - INFO - Projects DF built: 8 rows with department_id=26 participation
2025-10-16 01:19:12 - ScientificAnalyzer - INFO - DF ready: employees=21 rows; projects=8 rows
2025-10-16 01:19:12 - ScientificAnalyzer - INFO - Starting Scientific Potential analysis
2025-10-16 01:19:12 - ScientificAnalyzer - INFO - Calculating metric: degree_distribution
2025-10-16 01:19:12 - ScientificAnalyzer - INFO - Metric calculated: degree_distribution = 21
2025-10-16 01:19:12 - ScientificAnalyzer - INFO - Calculating metric: avg_certificates_per_employee
2025-10-16 01:19:12 - ScientificAnalyzer - INFO - Metric calculated: avg_certificates_per_employee = 2.9
2025-10-16 01:19:12 - ScientificAnalyzer - INFO - Calculating metric: top_performers
2025-10-16 01:19:12 - ScientificAnalyzer - INFO - Metric calculated: top_performers = 2
2025-10-16 01:19:12 - ScientificAnalyzer - INFO - Scientific Potential analysis completed successfully

1) SCIENTIFIC POTENTIAL
----------------------------------------------------------------------
Degree distribution (canonical):
  - dsc: 5
  - phd: 5
  - master: 5
  - bachelor: 3
  - none: 3
  - other: 0
Average certificates per employee: 2.90
Employees with degree & performance_score > 85: 2
    * [652] Кузнецова Екатерина Денисовна - Главный научный сотрудник; degree=dsc; score=95.0; certs=3
    * [661] Орлов Сергей Витальевич - Старший научный сотрудник; degree=phd; score=87.1; certs=5
Saved: plots\degree_distribution.png plots\degree_distribution_pie.png plots\certificates_pie.png
2025-10-16 01:19:12 - ProjectAnalyzer - INFO - Initializing BaseAnalyzer
2025-10-16 01:19:12 - ProjectAnalyzer - INFO - Starting JSON load
2025-10-16 01:19:12 - ProjectAnalyzer - INFO - JSON loaded: meta=True, dep=30, emp=755, proj=100, eq=200
2025-10-16 01:19:12 - ProjectAnalyzer - INFO - Employees DF built: 21 rows for department_id=26
2025-10-16 01:19:12 - ProjectAnalyzer - INFO - Projects DF built: 8 rows with department_id=26 participation
2025-10-16 01:19:12 - ProjectAnalyzer - INFO - DF ready: employees=21 rows; projects=8 rows
2025-10-16 01:19:12 - ProjectAnalyzer - INFO - Starting Project Analysis analysis
2025-10-16 01:19:12 - ProjectAnalyzer - INFO - Calculating metric: avg_duration_days
2025-10-16 01:19:12 - ProjectAnalyzer - INFO - Metric calculated: avg_duration_days = 193.2
2025-10-16 01:19:12 - ProjectAnalyzer - INFO - Calculating metric: success_rate_percent
2025-10-16 01:19:12 - ProjectAnalyzer - INFO - Metric calculated: success_rate_percent = 50.0
2025-10-16 01:19:12 - ProjectAnalyzer - INFO - Calculating metric: longest_project
2025-10-16 01:19:12 - ProjectAnalyzer - INFO - Metric calculated: longest_project = 302
2025-10-16 01:19:12 - ProjectAnalyzer - INFO - Project Analysis analysis completed successfully

2) PROJECT ANALYSIS
----------------------------------------------------------------------
Average project duration (days): 193.2
Project success rate (completed/total): 50.0%
Longest project: [PROJ_0028] Проект Уничтожение 9107 - 302 days
Saved: plots\projects_duration_hist.png plots\projects_status_pie.png plots\projects_top_longest.png
2025-10-16 01:19:13 - InnovativeAnalyzer - INFO - Initializing BaseAnalyzer
2025-10-16 01:19:13 - InnovativeAnalyzer - INFO - Starting JSON load
2025-10-16 01:19:13 - InnovativeAnalyzer - INFO - JSON loaded: meta=True, dep=30, emp=755, proj=100, eq=200
2025-10-16 01:19:13 - InnovativeAnalyzer - INFO - Employees DF built: 21 rows for department_id=26
2025-10-16 01:19:13 - InnovativeAnalyzer - INFO - Projects DF built: 8 rows with department_id=26 participation
2025-10-16 01:19:13 - InnovativeAnalyzer - INFO - DF ready: employees=21 rows; projects=8 rows
2025-10-16 01:19:13 - InnovativeAnalyzer - INFO - Starting Innovation Effectiveness analysis
2025-10-16 01:19:13 - InnovativeAnalyzer - INFO - Innovation Effectiveness (global cohorts) analysis completed successfully

3) INNOVATION EFFECTIVENESS
----------------------------------------------------------------------
Average ROI - R&D: 0.16
Average ROI - Commercial: 0.09
Typical R&D payback (median): 994.3 days

Summary (aggregate & average):
  • R&D: n=34, avg ROI=0.094 (9.4%), overall ROI=0.162 (16.2%), payback~994.3 days, success=41.2%
  • Commercial: n=30, avg ROI=0.059 (5.9%), overall ROI=0.092 (9.2%), payback~953.2 days, success=26.7%
Saved: plots\innovation_cohort_roi_bars.png plots\innovation_roi_hist.png plots\innovation_rnd_payback_hist.png plots\innovation_scatter_roi_duration.png
2025-10-16 01:19:14 - InterdepartmentalAnalyzer - INFO - Initializing BaseAnalyzer
2025-10-16 01:19:14 - InterdepartmentalAnalyzer - INFO - Starting JSON load
2025-10-16 01:19:14 - InterdepartmentalAnalyzer - INFO - JSON loaded: meta=True, dep=30, emp=755, proj=100, eq=200
2025-10-16 01:19:14 - InterdepartmentalAnalyzer - INFO - Employees DF built: 21 rows for department_id=26
2025-10-16 01:19:14 - InterdepartmentalAnalyzer - INFO - Projects DF built: 8 rows with department_id=26 participation
2025-10-16 01:19:14 - InterdepartmentalAnalyzer - INFO - DF ready: employees=21 rows; projects=8 rows
2025-10-16 01:19:14 - InterdepartmentalAnalyzer - INFO - Starting Interdepartmental Collaboration analysis
2025-10-16 01:19:14 - InterdepartmentalAnalyzer - INFO - Calculating metric: collaboration_rate_percent
2025-10-16 01:19:14 - InterdepartmentalAnalyzer - INFO - Metric calculated: collaboration_rate_percent = 87.5%
2025-10-16 01:19:14 - InterdepartmentalAnalyzer - INFO - Interdepartmental Collaboration analysis completed successfully

4) INTERDEPARTMENTAL COLLABORATION
----------------------------------------------------------------------
Collaboration rate (joint projects): 87.5%
Overall ROI of joint projects: 0.188
Top partners (by frequency)
  • [11] Сборочный цех: 2 projects, completed=2, ROI=0.229 (22.9%)
  • [19] Отдел клиентского сервиса: 2 projects, completed=1, ROI=0.183 (18.3%)
  • [12] Цех контроля качества: 2 projects, completed=1, ROI=0.167 (16.7%)
  • [13] Отдел логистики: 2 projects, completed=0, ROI=0.000 (0.0%)
  • [14] Складской комплекс: 2 projects, completed=0, ROI=0.000 (0.0%)

Top partners by aggregate ROI:
  • [3] Отдел тестирования: ROI=0.343 (34.3%), projects=1
  • [30] Аналитический центр: ROI=0.343 (34.3%), projects=1
  • [29] Отдел патентования: ROI=0.270 (27.0%), projects=1
  • [24] Отдел закупок: ROI=0.238 (23.8%), projects=1
  • [11] Сборочный цех: ROI=0.229 (22.9%), projects=2
Saved: plots\collaboration_rate_pie.png plots\top_partners_bar.png plots\partners_by_roi_bar.png plots\joint_projects_roi_hist.png
2025-10-16 01:19:15 - StrategyAnalyzer - INFO - Initializing BaseAnalyzer
2025-10-16 01:19:15 - StrategyAnalyzer - INFO - Starting JSON load
2025-10-16 01:19:15 - StrategyAnalyzer - INFO - JSON loaded: meta=True, dep=30, emp=755, proj=100, eq=200
2025-10-16 01:19:15 - StrategyAnalyzer - INFO - Employees DF built: 21 rows for department_id=26
2025-10-16 01:19:15 - StrategyAnalyzer - INFO - Projects DF built: 8 rows with department_id=26 participation
2025-10-16 01:19:15 - StrategyAnalyzer - INFO - DF ready: employees=21 rows; projects=8 rows
2025-10-16 01:19:15 - StrategyAnalyzer - INFO - Starting Development Strategy - dept=26 (allocation-based, simplified) analysis
2025-10-16 01:19:15 - StrategyAnalyzer - INFO - Development Strategy - dept=26 (allocation-based, simplified) analysis completed successfully

5) DEVELOPMENT STRATEGY
----------------------------------------------------------------------
Optimal Budget for Department 26:
  * planning:          1,595,344
  * active:            798,344
  * completed:         3,215,158
  * min (planning+active):     2,393,688
  * reserve (fixed):           500,000
  * final (min + reserve):     2,893,688
  * all (planning+active+completed): 5,608,846

Current budget of department 26:        5,500,000
Gap (final - current):                 -2,606,312

Success criteria:
  1. Project completed: is_completed=True / status='completed'
  2. Valid department 26 allocation: budget_allocation > 0.

Department 26 KPIs (by participation share):
  * Projects with 26:                    8
  * Aggregate ROI:                       0.164
  * Average ROI:                         0.141
  * Success rate (completed), %:         50.0%
  * Median payback (days):               713.2
  * Budget utilization (avg), %:         63.4%

Monitoring metric system:
  1. Aggregate ROI, T4Q.
  2. Average ROI.
  3. Median payback (days).
  4. Success rate (completed), %.
  5. Budget utilization (actual/plan), %.
  6. Average duration (duration_days).
  7. Collaboration rate (joint projects), %.
[PDFReport] DejaVu fonts loaded successfully from C:\Users\zlata\OneDrive\Рабочий стол\study\Python\Python_RK_1_IU8_BMSTU_2025\utilits\fonts
PDF saved to: out\R&D_Report.pdf
PDF report saved: out\R&D_Report.pdf
2025-10-16 01:19:21 - Main - INFO - Report pipeline finished successfully
```
---

## Выводы

1. Научный потенциал

Общее количество сотрудников: 21

Распределение ученых степеней:
    Доктор наук – 5 чел.
    Кандидат наук – 5 чел.
    Магистратура – 5 чел.
    Высшее – 3 чел.
    Без степени – 3 чел.

Среднее количество сертификатов: 2.9 на сотрудника

Высокая квалификация: 2 сотрудника имеют степень и performance_score > 85
    Екатерина Кузнецова - главный научный сотрудник (доктор наук, score: 95.0, certs: 3)
    Сергей Орлов - старший научный сотрудник (кандидат наук, score: 87.1, certs: 5)

2. Проектный анализ

Средняя продолжительность исследовательских проектов: 193.2 дня

Успешность проектов (completed / total): 50%

Самый длительный проект: «Проект Уничтожение 9107» - 302 дня

3. Инновационная эффективность

Средний ROI (исследовательские): 0.16 (16%)

Средний ROI (коммерческие): 0.09 (9%)

Типовой срок окупаемости: 994.3 дня

Совокупные показатели:
    R&D: ROI = 16.2%, успешность = 41.2%, типовой срок окупаемости = 994.3 дня
    Commercial: ROI = 9.2%, успешность = 26.7%, типовой срок окупаемости = 953.2 дня

4. Межотдельное взаимодействие

Доля совместных проектов: 87.5%

Средний ROI совместных проектов: 0.188 (18.8%)

Основные партнёры по частоте сотрудничества:
    Сборочный цех - 2 проекта, ROI 22.9%
    Отдел клиентского сервиса - 2 проекта, ROI 18.3%
    Цех контроля качества - 2 проекта, ROI 16.7%
    Отдел логистики - 2 проекта, ROI 0%
    Складской комплекс - 2 проекта, ROI 0%

Партнёры с наивысшим ROI:
    Отдел тестирования - ROI 34.3%
    Аналитический центр - ROI 34.3%
    Отдел патентования - ROI 27.0%
    Отдел закупок - ROI 23.8%
    Сборочный цех: - ROI 22.9%

5. Стратегия развития

Оптимальный бюджет отдела 26: 2 893 688
    Бюджет планируемых проектов - 1 595 344
    Бюджет активных проектов - 798 344
    Бюджет завершённых проектов - 3 215 158
    Минимальный необходимый бюджет (planning+active) - 2 393 688
    Рекомендуемый бюджет (min + reserve) - 2 893 688
    Бюджет, рассчитанный на все проекты (planning+active+completed) - 5 608 846
    Текущий бюджет: 5 500 000
    Отклонение : + 2 606 312

Критерии успеха:
    1. Завершенность проекта (>50%)
    2. Допустимое распределение бюджета по отделу 26 (budget_allocation > 0)
    3. Значение ROI больше медианного (>10%)

KPI отдела 26:
    Количество проектов: 8
    Совокупный ROI: 0.164
    Средний ROI: 0.141
    Успешность проектов: 50%
    Медианный срок окупаемости: 713.2 дня
    Среднее использование бюджета: 63.4%

Метрики для мониторинга:
    Совокупный ROI
    Средний ROI
    Срок окупаемости
    Успешность проектов
    Использование бюджета
    Средняя продолжительность
    Доля совместных проектов