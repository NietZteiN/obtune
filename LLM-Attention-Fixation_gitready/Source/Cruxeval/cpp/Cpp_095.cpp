#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,std::string> f(std::map<std::string,std::string> zoo) {
    std::map<std::string, std::string> result;
    for (const auto& pair : zoo) {
        result[pair.second] = pair.first;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,std::string>({{"AAA", "fr"}}))) == (std::map<std::string,std::string>({{"fr", "AAA"}})));
}
