#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    return text.append(text.size() + 1 - text.size(), '#');
}
int main() {
    auto candidate = f;
    assert(candidate(("the cow goes moo")) == ("the cow goes moo#"));
}
