---
name: audit
description: Run the 31-point performance audit on this project and report status, priority and impact for each point, measuring before changing anything.
disable-model-invocation: true
argument-hint: "[page, endpoint or area to focus on]"
---

# Audit

Load the `performance-optimization` skill with the Skill tool
(`wolfin-senior:performance-optimization`) and run Phases 1 to 4 (scope,
inspect, baseline measurement, report) for:

$ARGUMENTS

With no argument, audit the whole project, starting with what users hit
most.

Stop after the Phase 4 report: every one of the 31 points marked applied,
needs work, missing, not applicable or unknown, with priority, expected
impact and the measurements behind it. Change nothing yet. Ask the user
which improvements to apply, then continue with Phase 5 one change at a
time.
