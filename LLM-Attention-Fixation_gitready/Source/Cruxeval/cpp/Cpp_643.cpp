#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string suffix) {
    if (text.substr(text.size() - suffix.size()) == suffix) {
        text = text.substr(0, text.size() - 1) + std::string(1, std::toupper(text.back()));
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("damdrodm"), ("m")) == ("damdrodM"));
}
