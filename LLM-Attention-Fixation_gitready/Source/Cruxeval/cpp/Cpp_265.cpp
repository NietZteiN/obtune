#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::map<long,long> d, long k) {
    std::map<long, long> new_d;
    for(auto pair : d) {
        if (pair.first < k) {
            new_d[pair.first] = pair.second;
        }
    }
    return new_d;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>({{1, 2}, {2, 4}, {3, 3}})), (3)) == (std::map<long,long>({{1, 2}, {2, 4}})));
}
