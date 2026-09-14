#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,std::string> f(std::vector<std::string> seq, std::string value) {
    std::map<std::string, std::string> roles;
    for (const auto& s : seq) {
        roles[s] = "north";
    }
    if (!value.empty()) {
        std::istringstream iss(value);
        std::string token;
        while (std::getline(iss, token, ',')) {
            roles[std::string(token)] = "north";
        }
    }
    return roles;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"wise king", (std::string)"young king"})), ("")) == (std::map<std::string,std::string>({{"wise king", "north"}, {"young king", "north"}})));
}
