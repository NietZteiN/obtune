#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s1, std::string s2) {
    if (s2.substr(s2.size() - s1.size()) == s1) {
        s2 = s2.substr(0, s2.size() - s1.size());
    }
    return s2;
}
int main() {
    auto candidate = f;
    assert(candidate(("he"), ("hello")) == ("hello"));
}
