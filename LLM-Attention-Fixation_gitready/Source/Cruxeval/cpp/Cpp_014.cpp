#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s) {
    s.erase(std::remove(s.begin(), s.end(), ' '), s.end());
    std::reverse(s.begin(), s.end());
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("   OOP   ")) == ("POO"));
}
