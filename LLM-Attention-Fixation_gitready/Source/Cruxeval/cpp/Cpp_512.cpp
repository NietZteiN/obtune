#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string s) {
    return s.length() == std::count(s.begin(), s.end(), '0') + std::count(s.begin(), s.end(), '1');
}
int main() {
    auto candidate = f;
    assert(candidate(("102")) == (false));
}
