#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> m) {
    std::reverse(m.begin(), m.end());
    return m;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-4, (long)6, (long)0, (long)4, (long)-7, (long)2, (long)-1}))) == (std::vector<long>({(long)-1, (long)2, (long)-7, (long)4, (long)0, (long)6, (long)-4})));
}
