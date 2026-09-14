#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::map<long,long> bag) {
    std::vector<long> values;
    for(auto const& pair: bag) {
        values.push_back(pair.second);
    }
    
    std::map<long, long> tbl;
    for (long v = 0; v < 100; ++v) {
        if (std::find(values.begin(), values.end(), v) != values.end()) {
            tbl[v] = std::count(values.begin(), values.end(), v);
        }
    }
    
    return tbl;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>({{0, 0}, {1, 0}, {2, 0}, {3, 0}, {4, 0}}))) == (std::map<long,long>({{0, 5}})));
}
