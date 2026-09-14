#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::map<long,long> aDict) {
    std::map<long,long> result;
    for(auto &it : aDict) {
        result[it.second] = it.first;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>({{1, 1}, {2, 2}, {3, 3}}))) == (std::map<long,long>({{1, 1}, {2, 2}, {3, 3}})));
}
