#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,std::vector<std::string>> f(std::map<std::string,std::vector<std::string>> a, std::map<std::string,std::string> b) {
    for (auto &it : b) {
        if (a.find(it.first) == a.end()) {
            a[it.first] = std::vector<std::string>{it.second};
        } else {
            a[it.first].push_back(it.second);
        }
    }
    return a;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,std::vector<std::string>>()), (std::map<std::string,std::string>({{"foo", "bar"}}))) == (std::map<std::string,std::vector<std::string>>({{"foo", std::vector<std::string>({(std::string)"bar"})}})));
}
