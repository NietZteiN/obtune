#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::vector<std::map<std::string,long>> commands) {
    std::map<std::string, long> d;
    for(auto c : commands) {
        for(auto it = c.begin(); it != c.end(); ++it) {
            d[it->first] = it->second;
        }
    }
    return d;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::map<std::string,long>>({(std::map<std::string,long>)std::map<std::string,long>({{"brown", 2}}), (std::map<std::string,long>)std::map<std::string,long>({{"blue", 5}}), (std::map<std::string,long>)std::map<std::string,long>({{"bright", 4}})}))) == (std::map<std::string,long>({{"brown", 2}, {"blue", 5}, {"bright", 4}})));
}
