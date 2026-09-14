#include <bits/stdc++.h>
std::string f(std::string text, std::string character) {
    if (text.empty() || text.back() != character.back()) {
        return f(character + text, character);
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("staovk"), ("k")) == ("staovk"));
}
