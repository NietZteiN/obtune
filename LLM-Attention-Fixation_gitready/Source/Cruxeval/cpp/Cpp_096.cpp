#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    return std::none_of(text.begin(), text.end(), [](char c){ return std::isupper(c); });
}
int main() {
    auto candidate = f;
    assert(candidate(("lunabotics")) == (true));
}
