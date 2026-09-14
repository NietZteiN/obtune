#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> L, long m, long start, long step) {
    L.insert(L.begin() + start, m);
    for (long x = start - 1; x > 0; x -= step) {
        start -= 1;
        auto it = std::find(L.begin(), L.end(), m);
        if (it != L.end()) {
            auto index = std::distance(L.begin(), it);
            L.insert(L.begin() + start, *(it - 1));
            L.erase(it - 1);
        }
    }
    return L;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)7, (long)9})), (3), (3), (2)) == (std::vector<long>({(long)1, (long)2, (long)7, (long)3, (long)9})));
}
