#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c){ return std::tolower(c); });
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("abcDEFGhIJ")) == ("abcdefghij"));
}
