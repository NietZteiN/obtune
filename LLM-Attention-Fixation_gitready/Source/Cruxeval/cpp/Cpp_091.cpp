#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::string s) {
    std::vector<std::string> keys;
    std::map<char, int> d;
    for (char c : s) {
        if (d.find(c) == d.end()) {
            keys.push_back(std::string(1, c));
            d[c] = 1;
        }
    }
    return keys;
}
int main() {
    auto candidate = f;
    assert(candidate(("12ab23xy")) == (std::vector<std::string>({(std::string)"1", (std::string)"2", (std::string)"a", (std::string)"b", (std::string)"3", (std::string)"x", (std::string)"y"})));
}
