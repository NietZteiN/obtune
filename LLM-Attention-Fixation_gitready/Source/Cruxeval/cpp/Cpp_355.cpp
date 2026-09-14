#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string prefix) {
    return text.substr(prefix.length());
}
int main() {
    auto candidate = f;
    assert(candidate(("123x John z"), ("z")) == ("23x John z"));
}
