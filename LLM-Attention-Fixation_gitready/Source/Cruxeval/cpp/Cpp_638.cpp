#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, std::string suffix) {
    if (suffix.empty()) {
        return s;
    }
    while (std::equal(s.rbegin(), s.rbegin() + suffix.size(), suffix.rbegin())) {
        s.erase(s.size() - suffix.size(), suffix.size());
    }
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("ababa"), ("ab")) == ("ababa"));
}
