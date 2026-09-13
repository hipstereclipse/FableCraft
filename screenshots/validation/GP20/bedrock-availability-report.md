# Pinned Bedrock server availability audit

No official pinned binary was acquired, extracted or executed. The sandbox
attempt failed DNS; an authorized escalated HTTPS attempt reached the official
host but its HTTP/2 stream reset; one HTTP/1.1 fallback timed out after 45.005
seconds with zero bytes. All requests retained certificate checking and allowed
only HTTPS, including at most three redirects. These are transport failures;
there was no HTTP response proving the pinned archive missing.

Candidate: https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.21.100.7.zip

The current official download-links API was readable through the web tool:
https://net-secondary.web.minecraft-services.net/api/v1.0/download/links
It lists Linux server 1.26.45.1, so it does not independently verify the candidate
1.21.100.7 URL. No newer or third-party binary was substituted.

The host reports x86_64 and glibc 2.44; curl, unzip, unshare, timeout and Python
are installed. Actual binary dependencies and server version/startup remain
untested. No server/world/port was created, no license agreement was accepted,
and no package or system configuration was changed. Network-namespace startup
was not attempted because no executable was obtained. Native facility acceptance
remains unrun.

See bedrock-availability-results.json, bedrock-availability-download-errors.log and the empty bedrock-availability-http1.headers /
bedrock-availability-http2.headers files for precise attempts and outcomes. The bounded attempt is complete. A next
engine run requires a successfully verified official pinned archive; repeating
these unchanged transport attempts is not a useful validation step.

The attempt originally ran in ignored tmp/conformance/bedrock-runtime-audit;
these copies preserve that observation for GP20. No new network request or
server execution was made when copying the evidence.
