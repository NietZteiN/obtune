#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::map<long,long> ets) {
    while (!ets.empty()) {
        auto kv = ets.rbegin();
        long k = kv->first;
        long v = kv->second;
        ets.erase(k);
        ets[k] = v * v;
    }
    return ets;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>())) == (std::map<long,long>()));
}
