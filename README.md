# arch2-orchestrator-smoketest

Throwaway repo used to live-test ARCH 2.0's CPU-orchestrator-pod feature
(see ArcadiaImpact/arch2#136) against real RunPod infrastructure. Not a
real research task — safe to delete once the test has been reviewed.

The eval computes the mean of `value` in `sample.csv`: public data means
3.0, held-out data means 20.0, so a worker can't just guess the answer
from the public sample alone.
