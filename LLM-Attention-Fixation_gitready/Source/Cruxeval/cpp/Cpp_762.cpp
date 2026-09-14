#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::transform(text.begin(), text.end(), text.begin(), ::tolower);
    std::string capitalize = text;
    capitalize[0] = std::toupper(capitalize[0]);
    return text.substr(0, 1) + capitalize.substr(1);
}
int main() {
    auto candidate = f;
    assert(candidate(("this And cPanel")) == ("this and cpanel"));
}
