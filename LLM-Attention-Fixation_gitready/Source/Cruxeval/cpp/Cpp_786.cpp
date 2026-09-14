#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string letter) {
    if (text.find(letter) != std::string::npos) {
        size_t start = text.find(letter);
        return text.substr(start + 1) + text.substr(0, start + 1);
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("19kefp7"), ("9")) == ("kefp719"));
}
