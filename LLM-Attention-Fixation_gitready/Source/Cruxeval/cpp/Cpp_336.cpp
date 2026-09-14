#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, std::string sep) {
    s += sep;
    return s.substr(0, s.rfind(sep));
}
int main() {
    auto candidate = f;
    assert(candidate(("234dsfssdfs333324314"), ("s")) == ("234dsfssdfs333324314"));
}
