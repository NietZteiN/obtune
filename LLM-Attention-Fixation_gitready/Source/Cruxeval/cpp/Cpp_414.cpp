#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,std::vector<std::string>> f(std::map<std::string,std::vector<std::string>> d) {
    std::map<std::string, std::vector<std::string>> dCopy = d;
    for(auto& pair : dCopy) {
        for(auto& str : pair.second) {
            std::transform(str.begin(), str.end(), str.begin(), ::toupper);
        }
    }
    return dCopy;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,std::vector<std::string>>({{"X", std::vector<std::string>({(std::string)"x", (std::string)"y"})}}))) == (std::map<std::string,std::vector<std::string>>({{"X", std::vector<std::string>({(std::string)"X", (std::string)"Y"})}})));
}
