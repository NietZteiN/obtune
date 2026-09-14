#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> a, std::vector<long> b) {
    std::sort(a.begin(), a.end());
    std::sort(b.begin(), b.end(), std::greater<>());
    a.insert(a.end(), b.begin(), b.end());
    return a;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)666})), (std::vector<long>())) == (std::vector<long>({(long)666})));
}
