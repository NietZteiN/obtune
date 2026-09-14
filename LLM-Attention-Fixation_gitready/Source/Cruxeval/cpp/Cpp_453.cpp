#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string string, std::string c) {
    return string.substr(string.size() - c.size()) == c;
}
int main() {
    auto candidate = f;
    assert(candidate(("wrsch)xjmb8"), ("c")) == (false));
}
