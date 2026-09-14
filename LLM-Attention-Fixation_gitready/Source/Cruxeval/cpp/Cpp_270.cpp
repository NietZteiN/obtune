#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::map<long,long> dic) {
    std::map<long,long> d;
    while (!dic.empty()) {
        d[dic.begin()->first] = dic.begin()->second;
        dic.erase(dic.begin());
    }
    return d;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>())) == (std::map<long,long>()));
}
