#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string value) {
    std::string new_text = text;
    try {
        new_text.append(value);
        int length = new_text.length();
        return "[" + std::to_string(length) + "]";
    } catch (...) {
        return "[0]";
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("abv"), ("a")) == ("[4]"));
}
