#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    if (std::isupper(text[0])) {
        if (text.length() > 1 && std::tolower(text[0]) != text[0]) {
            return std::string(1, std::tolower(text[0])) + text.substr(1);
        }
    } else if (std::isalpha(text[0])) {
        text[0] = std::toupper(text[0]);
        for (int i = 1; i < text.length(); ++i) {
            text[i] = std::tolower(text[i]);
        }
        return text;
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("")) == (""));
}
