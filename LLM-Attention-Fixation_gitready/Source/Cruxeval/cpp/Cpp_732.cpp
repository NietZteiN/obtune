#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::map<std::string,long> char_freq) {
    std::map<std::string, long> result;
    for(auto& pair : char_freq) {
        result[pair.first] = pair.second / 2;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"u", 20}, {"v", 5}, {"b", 7}, {"w", 3}, {"x", 3}}))) == (std::map<std::string,long>({{"u", 10}, {"v", 2}, {"b", 3}, {"w", 1}, {"x", 1}})));
}
