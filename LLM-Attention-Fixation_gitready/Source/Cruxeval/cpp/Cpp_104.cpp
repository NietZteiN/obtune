#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::string text) {
    std::map<std::string, long> dic;
    for (char& c : text) {
        dic[std::string(1, c)] = dic[std::string(1, c)] + 1;
    }
    for (auto& pair : dic) {
        if (pair.second > 1) {
            pair.second = 1;
        }
    }
    return dic;
}
int main() {
    auto candidate = f;
    assert(candidate(("a")) == (std::map<std::string,long>({{"a", 1}})));
}
