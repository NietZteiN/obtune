#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::map<std::string,long> d) {
    std::vector<std::string> l;
    while (!d.empty()) {
        std::string key = d.rbegin()->first;
        d.erase(key);
        l.push_back(key);
    }
    return l;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"f", 1}, {"h", 2}, {"j", 3}, {"k", 4}}))) == (std::vector<std::string>({(std::string)"k", (std::string)"j", (std::string)"h", (std::string)"f"})));
}
