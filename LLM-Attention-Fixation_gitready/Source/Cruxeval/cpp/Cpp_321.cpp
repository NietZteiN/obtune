#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::map<std::string,long> update, std::map<std::string,long> starting) {
    std::map<std::string, long> d = starting;
    for (const auto& pair : update) {
        if (d.find(pair.first) != d.end()) {
            d[pair.first] += pair.second;
        } else {
            d[pair.first] = pair.second;
        }
    }
    return d;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>()), (std::map<std::string,long>({{"desciduous", 2}}))) == (std::map<std::string,long>({{"desciduous", 2}})));
}
