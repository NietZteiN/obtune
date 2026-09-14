#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string suffix) {
    text += suffix;
    while(text.substr(text.length() - suffix.length(), suffix.length()) == suffix) {
        text = text.substr(0, text.length() - 1);
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("faqo osax f"), ("f")) == ("faqo osax "));
}
