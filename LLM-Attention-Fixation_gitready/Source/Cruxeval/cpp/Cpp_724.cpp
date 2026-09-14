#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::string text, std::string function) {
    std::vector<long> cites = {static_cast<long>(text.substr(text.find(function) + function.size()).size())};
    for (char char_ : text) {
        std::string s(1, char_);
        if (s == function) {
            cites.push_back(static_cast<long>(text.substr(text.find(function) + function.size()).size()));
        }
    }
    return cites;
}
int main() {
    auto candidate = f;
    assert(candidate(("010100"), ("010")) == (std::vector<long>({(long)3})));
}
