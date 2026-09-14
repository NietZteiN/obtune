#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    int length = text.length() / 2;
    std::string left_half = text.substr(0, length);
    std::string right_half = text.substr(length);
    std::reverse(right_half.begin(), right_half.end());
    return left_half + right_half;
}
int main() {
    auto candidate = f;
    assert(candidate(("n")) == ("n"));
}
