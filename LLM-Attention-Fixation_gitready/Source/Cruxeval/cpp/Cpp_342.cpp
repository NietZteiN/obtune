#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    return std::count(text.begin(), text.end(), '-') == text.length();
}
int main() {
    auto candidate = f;
    assert(candidate(("---123-4")) == (false));
}
