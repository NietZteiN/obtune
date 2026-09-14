#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, std::string from_c, std::string to_c) {
    std::transform(s.begin(), s.end(), s.begin(), [from_c, to_c](char c) { 
        size_t pos = from_c.find(c);
        return pos != std::string::npos ? to_c[pos] : c; 
    });
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("aphid"), ("i"), ("?")) == ("aph?d"));
}
