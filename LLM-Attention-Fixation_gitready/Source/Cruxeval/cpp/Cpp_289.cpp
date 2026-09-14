#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string code) {
    std::string encoded = "b'" + code + "'";
    return code + ": " + encoded;
}
int main() {
    auto candidate = f;
    assert(candidate(("148")) == ("148: b'148'"));
}
