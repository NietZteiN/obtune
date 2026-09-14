#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,std::vector<std::string>> f(std::map<std::string,std::string> countries) {
    std::map<std::string, std::vector<std::string>> language_country;
    for (const auto& pair : countries) {
        if (language_country.find(pair.second) == language_country.end()) {
            language_country[pair.second] = std::vector<std::string>();
        }
        language_country[pair.second].push_back(pair.first);
    }
    return language_country;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,std::string>())) == (std::map<std::string,std::vector<std::string>>()));
}
