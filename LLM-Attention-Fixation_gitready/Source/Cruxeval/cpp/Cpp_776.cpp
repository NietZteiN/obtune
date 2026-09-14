#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::map<long,long> dictionary) {
    std::map<std::string, long> a;
    for (auto iter = dictionary.begin(); iter != dictionary.end(); ++iter) {
        if (iter->first % 2 != 0) {
            a['$' + std::to_string(iter->first)] = iter->second;
        }
    }
    return a;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>())) == (std::map<std::string,long>()));
}
