#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, std::string c) {
    int count = std::count(s.begin(), s.end(), c[0]);
    std::string base = std::string(count + 1, c[0]);
    if (s.size() >= base.size() && s.substr(s.size() - base.size()) == base) {
        s.erase(s.size() - base.size());
    }
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("mnmnj krupa...##!@#!@#$$@##"), ("@")) == ("mnmnj krupa...##!@#!@#$$@##"));
}
