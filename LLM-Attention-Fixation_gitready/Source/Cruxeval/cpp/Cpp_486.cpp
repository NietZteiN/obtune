#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::map<long,long> dic) {
    std::map<long, long> dic_op = dic;
    for(auto& kv : dic_op) {
        dic_op[kv.first] = kv.second * kv.second;
    }
    return dic_op;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>({{1, 1}, {2, 2}, {3, 3}}))) == (std::map<long,long>({{1, 1}, {2, 4}, {3, 9}})));
}
