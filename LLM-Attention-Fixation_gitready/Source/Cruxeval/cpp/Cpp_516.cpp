#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> strings, std::string substr) {
    std::vector<std::string> result;
    for(const auto &s : strings) {
        if(s.find(substr) == 0) {
            result.push_back(s);
        }
    }
    std::sort(result.begin(), result.end(), [](const std::string &a, const std::string &b) {
        return a.length() < b.length();
    });
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"condor", (std::string)"eyes", (std::string)"gay", (std::string)"isa"})), ("d")) == (std::vector<std::string>()));
}
