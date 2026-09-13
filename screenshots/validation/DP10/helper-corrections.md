# DP10 helper corrections

No base validation gate failed and no production source was changed for these corrections.

The first diagnostics launch used snapshot cwd while trying to read a repository-relative scratch helper. Creation and launch both failed before any diagnostic ran. The tool transcript retains the actual traceback; diagnostics-launch-initial.log is an explicitly labelled summary. Creating the helper from repository cwd and launching it in the reviewed snapshot passed all three diagnostics.

The second review's extra fixture returned a source point from inside(); its first assertion treated that point as a ticket. Five probes passed and that assertion failed. The corrected helper reads the actual saved ticket, and all six pass. Both original/final logs remain. No owner change was made.

The second review's final hash guard observed that the first reviewer had added a crypto import and source-hash log to a shared ignored helper. Removing exactly those two lines reproduced the original helper hash. Original and corrected hashes and the comparison are retained. Curated portable independent helpers require explicit predecessor source for baseline probes, derive actual geometry through Python and never spawn Git. The final portable 22-case review and six extra probes pass.
