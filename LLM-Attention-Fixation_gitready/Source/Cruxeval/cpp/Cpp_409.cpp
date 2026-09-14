#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string prefix) {
    if (!text.empty()) {
        size_t pos = text.find(prefix);
        if (pos == 0) {
            text = text.substr(prefix.length());
        }
        std::transform(text.begin(), text.begin() + 1, text.begin(), ::tolower);
        std::transform(text.end() - 1, text.end(), text.end() - 1, ::toupper);
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("querist"), ("u")) == ("querisT"));
}
