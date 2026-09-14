#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,std::vector<std::string>> f(std::vector<std::string> l1, std::vector<std::string> l2) {
    std::map<std::string, std::vector<std::string>> result;

    if (l1.size() != l2.size()) {
        return result;
    }

    for (const std::string& s : l1) {
        result[s] = l2;
    }

    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"a", (std::string)"b"})), (std::vector<std::string>({(std::string)"car", (std::string)"dog"}))) == (std::map<std::string,std::vector<std::string>>({{"a", std::vector<std::string>({(std::string)"car", (std::string)"dog"})}, {"b", std::vector<std::string>({(std::string)"car", (std::string)"dog"})}})));
}
