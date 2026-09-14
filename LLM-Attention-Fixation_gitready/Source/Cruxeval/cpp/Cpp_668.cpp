#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    return text.substr(text.size() - 1) + text.substr(0, text.size() - 1);
}
int main() {
    auto candidate = f;
    assert(candidate(("hellomyfriendear")) == ("rhellomyfriendea"));
}
