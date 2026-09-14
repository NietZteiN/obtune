#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s) {
    return s.substr(3) + s[2] + s.substr(5, 3);
}
int main() {
    auto candidate = f;
    assert(candidate(("jbucwc")) == ("cwcuc"));
}
