#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s) {
    s.erase(std::find_if(s.rbegin(), s.rend(), [](int ch) {
        return !std::isspace(ch);
    }).base(), s.end());
    std::reverse(s.begin(), s.end());
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("ab        ")) == ("ba"));
}
