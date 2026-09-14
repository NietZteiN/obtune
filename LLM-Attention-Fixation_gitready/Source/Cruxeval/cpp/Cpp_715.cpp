#include <assert.h>
#include <bits/stdc++.h>
bool f(std::string text, std::string character) {
    return std::count(text.begin(), text.end(), character[0]) % 2 != 0;
}
int main() {
    auto candidate = f;
    assert(candidate(("abababac"), ("a")) == (false));
}
