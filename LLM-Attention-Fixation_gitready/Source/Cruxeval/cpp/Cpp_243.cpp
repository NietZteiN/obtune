#include <assert.h>
#include <bits/stdc++.h>

bool f(std::string text, std::string character) {
    return std::islower(character[0]) && std::all_of(text.begin(), text.end(), [](char c) { return std::islower(c); });
}
int main() {
    auto candidate = f;
    assert(candidate(("abc"), ("e")) == (true));
}
