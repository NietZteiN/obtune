#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long length, std::string fillchar) {
    if (length <= text.length()) {
        return text;
    }
    long padding = length - text.length();
    long left_padding = padding / 2 + (padding % 2 != 0);
    return std::string(left_padding, fillchar[0]) + text + std::string(padding / 2, fillchar[0]);
}
int main() {
    auto candidate = f;
    assert(candidate(("magazine"), (25), (".")) == (".........magazine........"));
}
