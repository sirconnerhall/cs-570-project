# cs-570-project
## Learning to Find Failure Cases for Algorithms
 
We use genetic algorithms to analyze input patterns that lead to "failure" of algorithms. Failure is defined by the respective fitness function of each algorithm.

The examples included in this repository are Quicksort, Djikstra's Algorithm, and Coin Change. The framework is extensible to other problems with apropriate failure definitions.

### Original Assignment:
> In this project, groups will select a non-trivial algorithm covered in the course and design an AI/ML model or heuristic that automatically generates or discovers input instances where the algorithm performs poorly (e.g., worst-case runtime, bad approximation quality, unstable behavior, or violated assumptions). The goal is to build a systematic “failure-finder” rather than manually crafting counterexamples. Students will evaluate the approach by measuring how reliably it finds hard cases compared to random testing and human-designed adversarial inputs, and then apply the same failure-finding framework to one or more additional algorithms to test generality. Projects will be assessed on the strength of the failure cases found, the rigor of evaluation, and how well the framework transfers across different algorithm families.
