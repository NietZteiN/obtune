#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    std::transform(text.begin(), text.end(), text.begin(), ::tolower);
    text[0] = std::toupper(text[0]);
    text[text.size() - 1] = std::toupper(text[text.size() - 1]);
    return std::all_of(text.begin(), text.end(), ::isupper);
}
int main() {
    auto candidate = f;
    assert(candidate(("Josh")) == (false));
}
