#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string s, std::string n) {
    return std::equal(s.begin(), s.end(), n.begin(), n.end(), [](char a, char b) {
        return std::tolower(a) == std::tolower(b);
    });
}
int main() {
    auto candidate = f;
    assert(candidate(("daaX"), ("daaX")) == (true));
}
