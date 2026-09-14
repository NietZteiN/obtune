#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s) {
    std::replace(s.begin(), s.end(), '(', '[');
    std::replace(s.begin(), s.end(), ')', ']');
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("(ac)")) == ("[ac]"));
}
