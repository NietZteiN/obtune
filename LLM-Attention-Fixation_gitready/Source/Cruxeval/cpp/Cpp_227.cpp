#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::transform(text.begin(), text.end(), text.begin(), ::tolower);
    char head = text[0];
    std::string tail = text.substr(1);
    std::string result = std::string(1, std::toupper(head)) + tail;
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("Manolo")) == ("Manolo"));
}
