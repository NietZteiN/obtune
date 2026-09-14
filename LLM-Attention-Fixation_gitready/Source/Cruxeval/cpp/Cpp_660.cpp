#include<assert.h>
#include<bits/stdc++.h>
long f(long num) {
    std::vector<long> initial = {1};
    std::vector<long> total = initial;
    for (long i = 0; i < num; i++) {
        total = {1};
        for (size_t j = 0; j < total.size() - 1; j++) {
            total.push_back(initial[j] + initial[j+1]);
        }
        initial.push_back(total.back());
    }

    long sum = 0;
    for (long val : initial) {
        sum += val;
    }

    return sum;
}
int main() {
    auto candidate = f;
    assert(candidate((3)) == (4));
}
