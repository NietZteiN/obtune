#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::map<std::string,long> obj) {
    for(auto& pair : obj) {
        if(pair.second >= 0) {
            pair.second = -pair.second;
        }
    }
    return obj;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"R", 0}, {"T", 3}, {"F", -6}, {"K", 0}}))) == (std::map<std::string,long>({{"R", 0}, {"T", -3}, {"F", -6}, {"K", 0}})));
}
