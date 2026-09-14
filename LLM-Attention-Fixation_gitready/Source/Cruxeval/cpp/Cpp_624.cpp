#include <assert.h>
#include <bits/stdc++.h>
std::string f(std::string text, std::string character) {
    size_t char_index = text.find(character);
    std::string result;
    if (char_index != std::string::npos) {
        result = text.substr(0, char_index);
    }
    result += character + text.substr(char_index + character.length());
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("llomnrpc"), ("x")) == ("xllomnrpc"));
}
