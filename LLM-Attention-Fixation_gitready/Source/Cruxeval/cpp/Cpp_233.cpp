#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> xs) {
    for (int idx = xs.size() - 2; idx >= 0; idx--) {
        xs.insert(xs.begin() + idx, xs[0]);
        xs.erase(xs.begin());
    }
    return xs;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3}))) == (std::vector<long>({(long)1, (long)2, (long)3})));
}
