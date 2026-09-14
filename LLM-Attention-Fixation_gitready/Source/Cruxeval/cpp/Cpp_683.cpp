#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::map<std::string,long> dict1, std::map<std::string,long> dict2) {
    std::map<std::string, long> result = dict1;
    for (const auto& pair : dict2) {
        result[pair.first] = pair.second;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"disface", 9}, {"cam", 7}})), (std::map<std::string,long>({{"mforce", 5}}))) == (std::map<std::string,long>({{"disface", 9}, {"cam", 7}, {"mforce", 5}})));
}
