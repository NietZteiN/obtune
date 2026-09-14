#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string insert) {
    std::unordered_set<char> whitespaces = {'\t', '\r', '\v', ' ', '\f', '\n'};
    std::string clean = "";
    for (char c : text) {
        if (whitespaces.find(c) != whitespaces.end()) {
            clean += insert;
        } else {
            clean += c;
        }
    }
    return clean;
}
int main() {
    auto candidate = f;
    assert(candidate(("pi wa"), ("chi")) == ("pichiwa"));
}
