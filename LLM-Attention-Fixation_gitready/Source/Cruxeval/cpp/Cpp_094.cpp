#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::map<std::string,long> a, std::map<std::string,long> b) {
    std::map<std::string, long> result = a;
    for (const auto& pair : b) {
        result[pair.first] = pair.second;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"w", 5}, {"wi", 10}})), (std::map<std::string,long>({{"w", 3}}))) == (std::map<std::string,long>({{"w", 3}, {"wi", 10}})));
}
