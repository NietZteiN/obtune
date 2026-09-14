#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::map<std::string,long> d) {
    std::vector<long> v(d.size(), 0);
    if (d.empty()) {
        return v;
    }
    
    int i = 0;
    for (const auto& kv : d) {
        v[i] = kv.second;
        i++;
    }

    return v;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"a", 1}, {"b", 2}, {"c", 3}}))) == (std::vector<long>({(long)1, (long)2, (long)3})));
}
