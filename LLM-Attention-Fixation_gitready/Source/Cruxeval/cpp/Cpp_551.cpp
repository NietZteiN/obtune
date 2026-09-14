#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::map<std::string,std::vector<std::string>> data) {
    std::vector<std::string> members;
    for (auto item : data) {
        for (auto member : item.second) {
            if (std::find(members.begin(), members.end(), member) == members.end()) {
                members.push_back(member);
            }
        }
    }
    std::sort(members.begin(), members.end());
    return members;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,std::vector<std::string>>({{"inf", std::vector<std::string>({(std::string)"a", (std::string)"b"})}, {"a", std::vector<std::string>({(std::string)"inf", (std::string)"c"})}, {"d", std::vector<std::string>({(std::string)"inf"})}}))) == (std::vector<std::string>({(std::string)"a", (std::string)"b", (std::string)"c", (std::string)"inf"})));
}
