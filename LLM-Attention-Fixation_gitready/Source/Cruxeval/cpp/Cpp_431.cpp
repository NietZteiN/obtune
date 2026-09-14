#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(long n, long m) {
    std::vector<long> arr;
    for(long i = 1; i <= n; i++) {
        arr.push_back(i);
    }
    for(long i = 0; i < m; i++) {
        arr.clear();
    }
    return arr;
}
int main() {
    auto candidate = f;
    assert(candidate((1), (3)) == (std::vector<long>()));
}
