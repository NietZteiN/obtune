#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string match, std::string fill, long n) {
    return fill.substr(0, n) + match;
}
int main() {
    auto candidate = f;
    assert(candidate(("9"), ("8"), (2)) == ("89"));
}
