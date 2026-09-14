#include <assert.h>
#include <bits/stdc++.h>

std::string f(std::string text, std::string character, std::string replace) {
    size_t pos = text.find(character);
    while (pos != std::string::npos) {
        text.replace(pos, character.length(), replace);
        pos = text.find(character, pos + replace.length());
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("a1a8"), ("1"), ("n2")) == ("an2a8"));
}
