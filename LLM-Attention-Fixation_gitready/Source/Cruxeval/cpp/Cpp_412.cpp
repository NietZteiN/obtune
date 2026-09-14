#include<assert.h>
#include<bits/stdc++.h>
long f(long start, long end, long interval) {
    std::vector<long> steps;
    for (long i = start; i <= end; i += interval) {
        steps.push_back(i);
    }
    if (std::find(steps.begin(), steps.end(), 1) != steps.end()) {
        steps.back() = end + 1;
    }
    return steps.size();
}
int main() {
    auto candidate = f;
    assert(candidate((3), (10), (1)) == (8));
}
