#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string new_text = text;
    while (text.length() > 1 && text[0] == text[text.length() - 1]) {
        new_text = text = text.substr(1, text.length() - 2);
    }
    return new_text;
}
int main() {
    auto candidate = f;
    assert(candidate((")")) == (")"));
}
