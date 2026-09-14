#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string test_str) {
    std::string s = test_str;
    std::replace(s.begin(), s.end(), 'a', 'A');
    std::replace(s.begin(), s.end(), 'e', 'A');
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("papera")) == ("pApArA"));
}
