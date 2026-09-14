#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<std::string> no) {
    std::unordered_map<std::string, bool> d;
    for(const std::string& str : no) {
        d[str] = false;
    }
    return d.size();
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"l", (std::string)"f", (std::string)"h", (std::string)"g", (std::string)"s", (std::string)"b"}))) == (6));
}
