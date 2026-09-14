#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string delim) {
    size_t pos = text.find(delim);
    std::string first = text.substr(0, pos);
    std::string second = text.substr(pos + delim.length());
    return second + delim + first;
}
int main() {
    auto candidate = f;
    assert(candidate(("bpxa24fc5."), (".")) == (".bpxa24fc5"));
}
