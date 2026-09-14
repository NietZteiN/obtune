#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(long k, long j) {
    std::vector<long> arr;
    for (long i = 0; i < k; i++) {
        arr.push_back(j);
    }
    return arr;
}
int main() {
    auto candidate = f;
    assert(candidate((7), (5)) == (std::vector<long>({(long)5, (long)5, (long)5, (long)5, (long)5, (long)5, (long)5})));
}
